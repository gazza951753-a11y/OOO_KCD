"""Timesheet period locking

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
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


def downgrade() -> None:
    op.drop_table("timesheet_periods")
