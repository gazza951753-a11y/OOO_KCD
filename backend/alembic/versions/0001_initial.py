"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    userrole = postgresql.ENUM("superadmin", "hr", "manager", "employee", name="userrole")
    userrole.create(op.get_bind(), checkfirst=True)

    timesheetstatus = postgresql.ENUM(
        "present", "absent", "vacation", "sick", "holiday", "business_trip",
        name="timesheetstatus"
    )
    timesheetstatus.create(op.get_bind(), checkfirst=True)

    documenttype = postgresql.ENUM(
        "vacation_request", "sick_leave", "reference", "other",
        name="documenttype"
    )
    documenttype.create(op.get_bind(), checkfirst=True)

    documentstatus = postgresql.ENUM(
        "draft", "pending", "approved", "rejected", "completed",
        name="documentstatus"
    )
    documentstatus.create(op.get_bind(), checkfirst=True)

    # departments (created before users due to FK)
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(300), nullable=False),
        sa.Column("role", sa.Enum("superadmin", "hr", "manager", "employee", name="userrole"), nullable=False),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("position", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # FK from departments.manager_id -> users.id
    op.create_foreign_key("fk_dept_manager", "departments", "users", ["manager_id"], ["id"])

    # timesheet_records
    op.create_table(
        "timesheet_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("check_in", sa.Time(), nullable=True),
        sa.Column("check_out", sa.Time(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("present", "absent", "vacation", "sick", "holiday", "business_trip", name="timesheetstatus"),
            nullable=False,
        ),
        sa.Column("work_hours", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # document_requests
    op.create_table(
        "document_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "type",
            sa.Enum("vacation_request", "sick_leave", "reference", "other", name="documenttype"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "pending", "approved", "rejected", "completed", name="documentstatus"),
            nullable=False,
        ),
        sa.Column("approver_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # document_templates
    op.create_table(
        "document_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column(
            "type",
            sa.Enum("vacation_request", "sick_leave", "reference", "other", name="documenttype"),
            nullable=False,
        ),
        sa.Column("template_content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("old_data", postgresql.JSONB(), nullable=True),
        sa.Column("new_data", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("document_templates")
    op.drop_table("document_requests")
    op.drop_table("timesheet_records")
    op.drop_constraint("fk_dept_manager", "departments", type_="foreignkey")
    op.drop_table("users")
    op.drop_table("departments")

    op.execute("DROP TYPE IF EXISTS documentstatus")
    op.execute("DROP TYPE IF EXISTS documenttype")
    op.execute("DROP TYPE IF EXISTS timesheetstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
