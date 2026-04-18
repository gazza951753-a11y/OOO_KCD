"""
Database initializer: creates all tables and types idempotently.
Uses create_all(checkfirst=True) so existing ENUMs/tables are silently skipped.
"""
import sys

from app.database import Base, engine
import app.models  # noqa: F401 — registers all ORM models with Base.metadata


def init_db() -> None:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("DB: schema OK")


if __name__ == "__main__":
    try:
        init_db()
    except Exception as exc:
        print(f"DB init failed: {exc}", file=sys.stderr)
        sys.exit(1)
