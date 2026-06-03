"""Link document to timesheet record

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        ALTER TABLE timesheet_records
        ADD COLUMN IF NOT EXISTS document_id INTEGER REFERENCES document_requests(id)
    """))
    conn.execute(sa.text("""
        ALTER TABLE timesheet_records
        ADD COLUMN IF NOT EXISTS requires_document BOOLEAN NOT NULL DEFAULT FALSE
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE timesheet_records DROP COLUMN IF EXISTS requires_document"
    ))
    conn.execute(sa.text(
        "ALTER TABLE timesheet_records DROP COLUMN IF EXISTS document_id"
    ))
