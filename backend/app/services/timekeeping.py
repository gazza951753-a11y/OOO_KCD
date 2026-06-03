from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.timekeeping import TimesheetRecord, TimesheetStatus
from app.schemas.timekeeping import TimesheetRecordCreate, TimesheetRecordUpdate, TimesheetSummary

DOCUMENT_REQUIRED_STATUSES = {
    TimesheetStatus.absent,
    TimesheetStatus.vacation,
    TimesheetStatus.sick,
    TimesheetStatus.business_trip,
}


def _compute_work_hours(record: TimesheetRecord) -> float | None:
    if record.check_in and record.check_out:
        from datetime import datetime as dt
        ci = dt.combine(date.today(), record.check_in)
        co = dt.combine(date.today(), record.check_out)
        delta = co - ci
        return round(delta.total_seconds() / 3600, 2) if delta.total_seconds() > 0 else 0.0
    return None


def _check_period_open(db: Session, record_date: date) -> None:
    from app.models.period import TimesheetPeriod
    period = db.query(TimesheetPeriod).filter(
        TimesheetPeriod.year == record_date.year,
        TimesheetPeriod.month == record_date.month,
    ).first()
    if period and period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Табельный период закрыт. Изменения невозможны.",
        )


def create_record(db: Session, data: TimesheetRecordCreate) -> TimesheetRecord:
    _check_period_open(db, data.date)
    if data.status in DOCUMENT_REQUIRED_STATUSES and not data.document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для данного статуса необходим документ-основание",
        )
    record = TimesheetRecord(**data.model_dump())
    record.requires_document = data.status in DOCUMENT_REQUIRED_STATUSES
    record.work_hours = _compute_work_hours(record)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record: TimesheetRecord, data: TimesheetRecordUpdate) -> TimesheetRecord:
    _check_period_open(db, record.date)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    if data.status is not None:
        record.requires_document = data.status in DOCUMENT_REQUIRED_STATUSES
    record.work_hours = _compute_work_hours(record)
    db.commit()
    db.refresh(record)
    return record


def approve_record(db: Session, record: TimesheetRecord, approver_id: int) -> TimesheetRecord:
    record.approved_by = approver_id
    record.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


def get_summary(db: Session, user_id: int, year: int, month: int) -> TimesheetSummary:
    from calendar import monthrange
    records = (
        db.query(TimesheetRecord)
        .filter(
            TimesheetRecord.user_id == user_id,
            TimesheetRecord.date >= date(year, month, 1),
            TimesheetRecord.date <= date(year, month, monthrange(year, month)[1]),
        )
        .all()
    )

    counts = {s: 0 for s in TimesheetStatus}
    total_hours = 0.0
    for r in records:
        counts[r.status] += 1
        total_hours += r.work_hours or 0.0

    return TimesheetSummary(
        user_id=user_id,
        month=month,
        year=year,
        total_days=len(records),
        present_days=counts[TimesheetStatus.present],
        absent_days=counts[TimesheetStatus.absent],
        vacation_days=counts[TimesheetStatus.vacation],
        sick_days=counts[TimesheetStatus.sick],
        holiday_days=counts[TimesheetStatus.holiday],
        business_trip_days=counts[TimesheetStatus.business_trip],
        total_work_hours=round(total_hours, 2),
    )
