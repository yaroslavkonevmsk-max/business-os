"""S3-compatible file uploader (Selectel, Yandex Cloud, AWS S3)."""

from __future__ import annotations

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)


class S3Uploader:
    """Upload files to S3-compatible object storage."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[boto3.client] = None

    @property
    def client(self) -> boto3.client:
        """Lazy-initialized boto3 S3 client."""
        if self._client is None:
            self._client = boto3.client(**self.settings.s3_client_config)
        return self._client

    def upload_file(
        self,
        local_path: str,
        s3_key: str,
        content_type: str = "application/pdf",
        extra_metadata: Optional[dict] = None,
    ) -> str:
        """Upload a local file to S3 and return the public URL.

        Args:
            local_path: Path to the local file.
            s3_key: S3 object key (path within bucket).
            content_type: MIME type of the file.
            extra_metadata: Optional S3 metadata dict.

        Returns:
            Public URL to the uploaded object.
        """
        try:
            upload_kwargs = {
                "Bucket": self.settings.s3_bucket,
                "Key": s3_key,
                "Body": open(local_path, "rb"),
                "ContentType": content_type,
            }
            if extra_metadata:
                upload_kwargs["Metadata"] = extra_metadata

            self.client.put_object(**upload_kwargs)
            logger.info("Uploaded %s to s3://%s/%s", local_path, self.settings.s3_bucket, s3_key)
        except ClientError as exc:
            logger.error("S3 upload failed: %s", exc)
            raise
        finally:
            upload_kwargs.get("Body", object()).close()  # type: ignore[union-attr]

        return self._build_url(s3_key)

    def upload_bytes(
        self,
        data: bytes,
        s3_key: str,
        content_type: str = "application/pdf",
        extra_metadata: Optional[dict] = None,
    ) -> str:
        """Upload bytes to S3 and return the public URL.

        Args:
            data: File bytes to upload.
            s3_key: S3 object key.
            content_type: MIME type.
            extra_metadata: Optional S3 metadata.

        Returns:
            Public URL to the uploaded object.
        """
        try:
            upload_kwargs = {
                "Bucket": self.settings.s3_bucket,
                "Key": s3_key,
                "Body": data,
                "ContentType": content_type,
            }
            if extra_metadata:
                upload_kwargs["Metadata"] = extra_metadata

            self.client.put_object(**upload_kwargs)
            logger.info("Uploaded bytes to s3://%s/%s", self.settings.s3_bucket, s3_key)
        except ClientError as exc:
            logger.error("S3 upload failed: %s", exc)
            raise

        return self._build_url(s3_key)

    def _build_url(self, s3_key: str) -> str:
        """Build public URL for an S3 object."""
        if self.settings.s3_public_url:
            return f"{self.settings.s3_public_url.rstrip('/')}/{s3_key}"

        endpoint = self.settings.s3_endpoint.rstrip("/")
        return f"{endpoint}/{self.settings.s3_bucket}/{s3_key}"

    def delete_file(self, s3_key: str) -> None:
        """Delete an object from S3."""
        try:
            self.client.delete_object(
                Bucket=self.settings.s3_bucket,
                Key=s3_key,
            )
            logger.info("Deleted s3://%s/%s", self.settings.s3_bucket, s3_key)
        except ClientError as exc:
            logger.error("S3 delete failed: %s", exc)
            raise
