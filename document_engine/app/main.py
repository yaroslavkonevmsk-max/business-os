"""Celery application entrypoint for the Document Engine."""

from __future__ import annotations

import logging
import os
from typing import Any

from celery import Celery
from celery.signals import task_failure, task_success

from app.config import get_settings
from app.generators.act_generator import ActGenerator
from app.generators.gph_generator import GPHGenerator
from app.generators.invoice_generator import InvoiceGenerator
from app.generators.report_generator import ReportGenerator
from app.generators.waybill_generator import WaybillGenerator
from app.uploaders.s3_uploader import S3Uploader
from app.utils.docx_to_pdf import convert_docx_to_pdf
from app.utils.number_to_words import amount_to_words

logger = logging.getLogger(__name__)

settings = get_settings()

app = Celery(
    "document_engine",
    broker=settings.broker_url,
    backend=settings.celery_result_backend,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=1,
    task_default_queue="documents",
    broker_connection_retry_on_startup=True,
)

GENERATOR_MAP = {
    "invoice": InvoiceGenerator,
    "act": ActGenerator,
    "waybill": WaybillGenerator,
    "gph_contract": GPHGenerator,
    "report": ReportGenerator,
}


def _prepare_context(data: dict[str, Any]) -> dict[str, Any]:
    """Enrich template context with computed fields."""
    ctx = dict(data)

    # Convert total_amount to words if present
    if "total_amount" in ctx:
        total = ctx["total_amount"]
        if isinstance(total, (int, float, str)):
            from decimal import Decimal
            try:
                total_dec = Decimal(str(total))
                ctx["total_amount_words"] = amount_to_words(total_dec)
            except Exception:
                ctx["total_amount_words"] = ""

    # Date formatting helpers
    if "document_date" in ctx and isinstance(ctx["document_date"], str):
        # Expect DD.MM.YYYY; keep as-is for templates
        pass

    # Prepayment calculations
    if "prepayment_percent" in ctx and "total_amount" in ctx:
        from decimal import Decimal
        try:
            total = Decimal(str(ctx["total_amount"]))
            percent = int(ctx["prepayment_percent"])
            prepayment = (total * Decimal(percent) / Decimal(100)).quantize(
                Decimal("0.01")
            )
            ctx["prepayment_amount"] = str(prepayment)
            ctx["remaining_amount"] = str(total - prepayment)
        except Exception:
            ctx["prepayment_amount"] = "0.00"
            ctx["remaining_amount"] = str(ctx["total_amount"])

    # Ensure items list exists
    if "items" not in ctx:
        ctx["items"] = []

    return ctx


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_document(
    self,
    document_id: int,
    document_type: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Generate a document from template, convert to PDF, upload to S3, notify backend.

    Args:
        document_id: Unique document ID in the backend.
        document_type: One of invoice, act, waybill, gph_contract, report.
        data: Template context variables.

    Returns:
        Dict with status and file_url.
    """
    logger.info(
        "Starting document generation: id=%s type=%s", document_id, document_type
    )

    try:
        generator_cls = GENERATOR_MAP.get(document_type)
        if not generator_cls:
            raise ValueError(f"Unknown document type: {document_type}")

        ctx = _prepare_context(data)

        # 1. Generate DOCX
        generator = generator_cls()
        docx_path = generator.generate(document_id, ctx)
        logger.info("DOCX generated: %s", docx_path)

        # 2. Convert to PDF
        pdf_path = convert_docx_to_pdf(
            docx_path,
            str(settings.temp_dir),
            libreoffice_path=settings.libreoffice_path,
        )
        logger.info("PDF generated: %s", pdf_path)

        # 3. Upload to S3
        s3_key = f"documents/{document_id}.pdf"
        uploader = S3Uploader()
        file_url = uploader.upload_file(pdf_path, s3_key)
        logger.info("File uploaded to S3: %s", file_url)

        # 4. Notify backend
        file_size = os.path.getsize(pdf_path)
        _notify_backend(document_id, file_url, file_size)

        # 5. Cleanup temp files
        try:
            os.remove(docx_path)
            os.remove(pdf_path)
        except OSError:
            logger.warning("Failed to cleanup temp files for document %s", document_id)

        return {
            "status": "success",
            "document_id": document_id,
            "file_url": file_url,
            "file_size": file_size,
        }

    except Exception as exc:
        logger.exception("Document generation failed: %s", exc)
        raise self.retry(exc=exc)


def _notify_backend(document_id: int, file_url: str, file_size: int) -> None:
    """Send completion notification to the backend API."""
    import requests

    url = f"{settings.backend_api_url}/api/v1/documents/{document_id}/generated"
    payload = {
        "file_url": file_url,
        "file_size": file_size,
        "status": "ready",
    }
    headers = {}
    if settings.backend_api_key:
        headers["X-API-Key"] = settings.backend_api_key

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Backend notified for document %s", document_id)
    except Exception as exc:
        logger.warning("Failed to notify backend for document %s: %s", document_id, exc)


@task_success.connect
@task_failure.connect
def log_task_result(sender: Any = None, **kwargs: Any) -> None:
    """Log task outcomes for monitoring."""
    if sender:
        logger.info("Task %s completed", sender.name)
