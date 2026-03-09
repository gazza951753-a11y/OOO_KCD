import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    hr = "hr"
    manager = "manager"
    employee = "employee"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    manager_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", use_alter=True, name="fk_dept_manager"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    manager: Mapped["User | None"] = relationship("User", foreign_keys=[manager_id], back_populates="managed_department")
    employees: Mapped[list["User"]] = relationship("User", foreign_keys="User.department_id", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.employee)
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department: Mapped["Department | None"] = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    managed_department: Mapped["Department | None"] = relationship("Department", foreign_keys=[Department.manager_id], back_populates="manager")

    timesheet_records: Mapped[list["TimesheetRecord"]] = relationship(  # type: ignore[name-defined]
        "TimesheetRecord", foreign_keys="TimesheetRecord.user_id", back_populates="user"
    )
    document_requests: Mapped[list["DocumentRequest"]] = relationship(  # type: ignore[name-defined]
        "DocumentRequest", foreign_keys="DocumentRequest.requester_id", back_populates="requester"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")  # type: ignore[name-defined]
