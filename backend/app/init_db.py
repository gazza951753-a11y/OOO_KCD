"""
Database initializer: creates all tables and types idempotently.
Uses create_all(checkfirst=True) so existing ENUMs/tables are silently skipped.
Applies incremental schema additions via ALTER TABLE IF NOT EXISTS.
"""
import sys

from sqlalchemy import text

from app.database import Base, engine
import app.models  # noqa: F401 — registers all ORM models with Base.metadata


def init_db() -> None:
    # Create all tables that don't yet exist (ENUMs are auto-handled with checkfirst)
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # Incremental additions — safe to run multiple times (IF NOT EXISTS / IF NOT EXISTS)
    with engine.connect() as conn:
        # 0002: document-timesheet link
        conn.execute(text(
            "ALTER TABLE timesheet_records "
            "ADD COLUMN IF NOT EXISTS document_id INTEGER REFERENCES document_requests(id)"
        ))
        conn.execute(text(
            "ALTER TABLE timesheet_records "
            "ADD COLUMN IF NOT EXISTS requires_document BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        # 0003: period locking table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS timesheet_periods (
                id SERIAL PRIMARY KEY,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                is_closed BOOLEAN NOT NULL DEFAULT FALSE,
                closed_at TIMESTAMP,
                closed_by INTEGER REFERENCES users(id),
                CONSTRAINT uq_period_year_month UNIQUE (year, month)
            )
        """))
        conn.commit()

    print("DB: schema OK")


if __name__ == "__main__":
    try:
        init_db()
    except Exception as exc:
        print(f"DB init failed: {exc}", file=sys.stderr)
        sys.exit(1)
