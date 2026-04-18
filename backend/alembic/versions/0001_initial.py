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
    conn = op.get_bind()

    # ENUM types — PostgreSQL CREATE TYPE has no IF NOT EXISTS, use DO blocks
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('superadmin', 'hr', 'manager', 'employee');
            END IF;
        END $$
    """))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'timesheetstatus') THEN
                CREATE TYPE timesheetstatus AS ENUM
                    ('present', 'absent', 'vacation', 'sick', 'holiday', 'business_trip');
            END IF;
        END $$
    """))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documenttype') THEN
                CREATE TYPE documenttype AS ENUM
                    ('vacation_request', 'sick_leave', 'reference', 'other');
            END IF;
        END $$
    """))
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documentstatus') THEN
                CREATE TYPE documentstatus AS ENUM
                    ('draft', 'pending', 'approved', 'rejected', 'completed');
            END IF;
        END $$
    """))

    # departments
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            manager_id INTEGER,
            created_at TIMESTAMP DEFAULT now()
        )
    """))

    # users
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(300) NOT NULL,
            role userrole NOT NULL,
            department_id INTEGER REFERENCES departments(id),
            position VARCHAR(200),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"
    ))

    # FK departments.manager_id -> users.id
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_dept_manager'
            ) THEN
                ALTER TABLE departments
                    ADD CONSTRAINT fk_dept_manager FOREIGN KEY (manager_id) REFERENCES users(id);
            END IF;
        END $$
    """))

    # timesheet_records
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS timesheet_records (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            date DATE NOT NULL,
            check_in TIME,
            check_out TIME,
            status timesheetstatus NOT NULL,
            work_hours FLOAT,
            comment TEXT,
            approved_by INTEGER REFERENCES users(id),
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT now()
        )
    """))

    # document_requests
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS document_requests (
            id SERIAL PRIMARY KEY,
            requester_id INTEGER NOT NULL REFERENCES users(id),
            type documenttype NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            status documentstatus NOT NULL,
            approver_id INTEGER REFERENCES users(id),
            approved_at TIMESTAMP,
            rejection_reason TEXT,
            file_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now()
        )
    """))

    # document_templates
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(300) NOT NULL,
            type documenttype NOT NULL,
            template_content TEXT NOT NULL,
            created_by INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT now()
        )
    """))

    # audit_logs
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            action VARCHAR(100) NOT NULL,
            entity_type VARCHAR(100) NOT NULL,
            entity_id INTEGER,
            old_data JSONB,
            new_data JSONB,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT now()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs (created_at)"
    ))


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
