import enum
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimesheetStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    vacation = "vacation"
    sick = "sick"
    holiday = "holiday"
    business_trip = "business_trip"


class TimesheetRecord(Base):
    __tablename__ = "timesheet_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[time | None] = mapped_column(Time, nullable=True)
    check_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[TimesheetStatus] = mapped_column(
        Enum(TimesheetStatus), nullable=False, default=TimesheetStatus.present
    )
    work_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("document_requests.id"), nullable=True
    )
    requires_document: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id], back_populates="timesheet_records"
    )
    approver: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by])  # type: ignore[name-defined]
    document: Mapped["DocumentRequest | None"] = relationship(  # type: ignore[name-defined]
        "DocumentRequest", foreign_keys=[document_id]
    )
