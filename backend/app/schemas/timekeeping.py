from datetime import date, datetime, time

from pydantic import BaseModel

from app.models.timekeeping import TimesheetStatus
from app.schemas.user import UserOut


class TimesheetRecordBase(BaseModel):
    date: date
    check_in: time | None = None
    check_out: time | None = None
    status: TimesheetStatus = TimesheetStatus.present
    comment: str | None = None


class TimesheetRecordCreate(TimesheetRecordBase):
    user_id: int


class TimesheetRecordUpdate(BaseModel):
    check_in: time | None = None
    check_out: time | None = None
    status: TimesheetStatus | None = None
    comment: str | None = None


class TimesheetRecordOut(TimesheetRecordBase):
    id: int
    user_id: int
    work_hours: float | None
    approved_by: int | None
    approved_at: datetime | None
    created_at: datetime
    user: UserOut | None = None

    model_config = {"from_attributes": True}


class TimesheetSummary(BaseModel):
    user_id: int
    month: int
    year: int
    total_days: int
    present_days: int
    absent_days: int
    vacation_days: int
    sick_days: int
    holiday_days: int
    business_trip_days: int
    total_work_hours: float
