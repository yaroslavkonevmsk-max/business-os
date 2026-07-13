"""Baseline migration: create all tables + triggers."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(32), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("ogrn", sa.String(15), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column(
            "tax_regime",
            sa.String(20),
            sa.CheckConstraint("tax_regime IN ('usn_income', 'usn_income_expense', 'npd', 'patent')"),
            nullable=True,
        ),
        sa.Column("bank_details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "tariff",
            sa.String(20),
            sa.CheckConstraint("tariff IN ('free', 'basic', 'pro', 'business')"),
            server_default=sa.text("'free'"),
            nullable=False,
        ),
        sa.Column("tariff_expires_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_users_telegram_id", "users", ["telegram_id"])
    op.create_index("idx_users_tariff", "users", ["tariff"])
    op.create_index("idx_users_inn", "users", ["inn"], postgresql_where=sa.text("inn IS NOT NULL"))

    # user_settings
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("morning_brief_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("morning_brief_time", sa.Time(), server_default=sa.text("'09:00:00'"), nullable=False),
        sa.Column("tax_reminders_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("language", sa.String(10), server_default=sa.text("'ru'"), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'RUB'"), nullable=False),
        sa.Column("timezone", sa.String(50), server_default=sa.text("'Europe/Moscow'"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # clients
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "type",
            sa.String(20),
            sa.CheckConstraint("type IN ('individual', 'company', 'ip')"),
            nullable=True,
        ),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("total_revenue", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("deals_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("first_payment_date", sa.Date(), nullable=True),
        sa.Column("last_payment_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("auto_created", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("source", sa.String(20), server_default=sa.text("'manual'"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_clients_user_id", "clients", ["user_id"])
    op.create_index("idx_clients_name", "clients", ["name"], postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"})
    op.create_index("idx_clients_inn", "clients", ["inn"], postgresql_where=sa.text("inn IS NOT NULL"))
    op.create_index("idx_clients_auto_created", "clients", ["user_id", "auto_created"])

    # bank_connections (before payments)
    op.create_table(
        "bank_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bank_code", sa.String(20), nullable=False),
        sa.Column("bank_name", sa.String(50), nullable=False),
        sa.Column("account_number", sa.String(50), nullable=True),
        sa.Column("account_mask", sa.String(20), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            sa.CheckConstraint("status IN ('active', 'expired', 'error')"),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("access_token_encrypted", postgresql.BYTEA(), nullable=False),
        sa.Column("refresh_token_encrypted", postgresql.BYTEA(), nullable=True),
        sa.Column("token_expires_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_sync_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_sync_error", sa.Text(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_bank_conn_user", "bank_connections", ["user_id"])
    op.create_index("idx_bank_conn_status", "bank_connections", ["user_id", "status"])
    op.create_index("idx_bank_conn_bank", "bank_connections", ["user_id", "bank_code"])

    # documents (before payments, without payment_id FK)
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "type",
            sa.String(20),
            sa.CheckConstraint("type IN ('invoice', 'act', 'waybill', 'gph_contract', 'report')"),
            nullable=False,
        ),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("total_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            sa.CheckConstraint("status IN ('draft', 'sent', 'paid', 'cancelled')"),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("payment_id", sa.Integer(), nullable=True),  # FK added later
        sa.Column("items", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "prepayment_percent",
            sa.Integer(),
            sa.CheckConstraint("prepayment_percent BETWEEN 0 AND 100"),
            nullable=True,
        ),
        sa.Column("sent_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("sent_method", sa.String(20), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_documents_user_id", "documents", ["user_id"])
    op.create_index("idx_documents_client_id", "documents", ["client_id"])
    op.create_index("idx_documents_type", "documents", ["user_id", "type"])
    op.create_index("idx_documents_date", "documents", ["user_id", "date"])
    op.create_index("idx_documents_number", "documents", ["user_id", "number"])
    op.create_unique_constraint("idx_documents_user_number", "documents", ["user_id", "number"])

    # payments (without document_id FK — cyclic dependency)
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bank_connection_id", sa.Integer(), sa.ForeignKey("bank_connections.id", ondelete="SET NULL"), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'RUB'"), nullable=False),
        sa.Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("parsed_client_name", sa.String(255), nullable=True),
        sa.Column("bank_transaction_id", sa.String(255), nullable=True),
        sa.Column("bank_name", sa.String(20), nullable=True),
        sa.Column(
            "payment_type",
            sa.String(10),
            sa.CheckConstraint("payment_type IN ('income', 'expense')"),
            server_default=sa.text("'income'"),
            nullable=False,
        ),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),  # FK added later
        sa.Column("is_tax_calculated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_payments_user_id", "payments", ["user_id"])
    op.create_index("idx_payments_client_id", "payments", ["client_id"], postgresql_where=sa.text("client_id IS NOT NULL"))
    op.create_index("idx_payments_date", "payments", ["user_id", "date"])
    op.create_index("idx_payments_bank_tx", "payments", ["bank_transaction_id"], postgresql_where=sa.text("bank_transaction_id IS NOT NULL"))
    op.create_index("idx_payments_type", "payments", ["user_id", "payment_type"])
    op.create_check_constraint("chk_payments_amount_positive", "payments", "amount > 0")

    # expenses
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("receipt_url", sa.String(500), nullable=True),
        sa.Column("ai_category", sa.String(50), nullable=True),
        sa.Column("is_manual_category", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_expenses_user_id", "expenses", ["user_id"])
    op.create_index("idx_expenses_date", "expenses", ["user_id", "date"])
    op.create_index("idx_expenses_category", "expenses", ["user_id", "category"])
    op.create_check_constraint("chk_expenses_amount_positive", "expenses", "amount > 0")

    # tax_calculations
    op.create_table(
        "tax_calculations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tax_regime", sa.String(20), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("total_income", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("total_expenses", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("tax_base", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("tax_amount", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("paid_amount", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("remaining_amount", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            sa.CheckConstraint("status IN ('pending', 'paid', 'overdue')"),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_unique_constraint("uq_tax_user_period_regime", "tax_calculations", ["user_id", "period", "tax_regime"])
    op.create_index("idx_tax_user_period", "tax_calculations", ["user_id", "period"])
    op.create_index("idx_tax_status", "tax_calculations", ["user_id", "status"])
    op.create_index("idx_tax_deadline", "tax_calculations", ["user_id", "deadline"], postgresql_where=sa.text("status = 'pending'"))

    # subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tariff", sa.String(20), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            sa.CheckConstraint("status IN ('active', 'cancelled', 'expired')"),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("payment_provider", sa.String(20), server_default=sa.text("'yookassa'"), nullable=False),
        sa.Column("payment_id", sa.String(255), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'RUB'"), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("auto_renew", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_subs_user", "subscriptions", ["user_id"])
    op.create_index("idx_subs_period", "subscriptions", ["user_id", "period_end"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_audit_user", "audit_log", ["user_id", "created_at"])
    op.create_index("idx_audit_action", "audit_log", ["action", "created_at"])

    # Add deferred FKs for cyclic dependency (payments <-> documents)
    op.create_foreign_key(
        "fk_documents_payment_id", "documents", "payments",
        ["payment_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_payments_document_id", "payments", "documents",
        ["document_id"], ["id"], ondelete="SET NULL"
    )

    # Triggers: update_updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    tables_with_updated_at = [
        "users", "user_settings", "clients", "payments", "expenses",
        "documents", "tax_calculations", "bank_connections", "subscriptions",
    ]
    for table in tables_with_updated_at:
        op.execute(
            f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
        )

    # Trigger: update_client_stats
    op.execute("""
        CREATE OR REPLACE FUNCTION update_client_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.client_id IS NOT NULL THEN
                UPDATE clients SET
                    total_revenue = (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE client_id = NEW.client_id AND payment_type = 'income'),
                    deals_count = (SELECT COUNT(*) FROM payments WHERE client_id = NEW.client_id AND payment_type = 'income'),
                    first_payment_date = (SELECT MIN(date::date) FROM payments WHERE client_id = NEW.client_id AND payment_type = 'income'),
                    last_payment_date = (SELECT MAX(date::date) FROM payments WHERE client_id = NEW.client_id AND payment_type = 'income'),
                    updated_at = NOW()
                WHERE id = NEW.client_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trigger_update_client_stats
        AFTER INSERT OR UPDATE OR DELETE ON payments
        FOR EACH ROW EXECUTE FUNCTION update_client_stats();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_update_client_stats ON payments;")
    op.execute("DROP FUNCTION IF EXISTS update_client_stats;")

    tables_with_updated_at = [
        "users", "user_settings", "clients", "payments", "expenses",
        "documents", "tax_calculations", "bank_connections", "subscriptions",
    ]
    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column;")

    # Drop FKs
    op.drop_constraint("fk_documents_payment_id", "documents", type_="foreignkey")
    op.drop_constraint("fk_payments_document_id", "payments", type_="foreignkey")

    # Drop tables in reverse dependency order
    op.drop_table("audit_log")
    op.drop_table("subscriptions")
    op.drop_table("tax_calculations")
    op.drop_table("expenses")
    op.drop_table("payments")
    op.drop_table("documents")
    op.drop_table("bank_connections")
    op.drop_table("clients")
    op.drop_table("user_settings")
    op.drop_table("users")
