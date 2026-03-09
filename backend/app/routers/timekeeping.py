from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_user, require_hr, require_manager
from app.database import get_db
from app.models.timekeeping import TimesheetRecord
from app.models.user import User, UserRole
from app.schemas.timekeeping import (
    TimesheetRecordCreate,
    TimesheetRecordOut,
    TimesheetRecordUpdate,
    TimesheetSummary,
)
from app.services import timekeeping as svc

router = APIRouter(prefix="/timesheet", tags=["timekeeping"])


def _get_record_or_404(db: Session, record_id: int) -> TimesheetRecord:
    rec = db.query(TimesheetRecord).filter(TimesheetRecord.id == record_id).first()
    if not rec:
        raise HTTPException(404, "Запись не найдена")
    return rec


@router.get("", response_model=list[TimesheetRecordOut])
def list_records(
    user_id: int | None = Query(None),
    department_id: int | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    q = db.query(TimesheetRecord).join(User, TimesheetRecord.user_id == User.id)
    # managers see only their department
    if current_user.role == UserRole.manager:
        q = q.filter(User.department_id == current_user.department_id)
    elif department_id:
        q = q.filter(User.department_id == department_id)

    if user_id:
        q = q.filter(TimesheetRecord.user_id == user_id)
    if date_from:
        q = q.filter(TimesheetRecord.date >= date_from)
    if date_to:
        q = q.filter(TimesheetRecord.date <= date_to)
    return q.order_by(TimesheetRecord.date.desc()).all()


@router.get("/me", response_model=list[TimesheetRecordOut])
def my_records(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(TimesheetRecord).filter(TimesheetRecord.user_id == current_user.id)
    if date_from:
        q = q.filter(TimesheetRecord.date >= date_from)
    if date_to:
        q = q.filter(TimesheetRecord.date <= date_to)
    return q.order_by(TimesheetRecord.date.desc()).all()


@router.post("", response_model=TimesheetRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    data: TimesheetRecordCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    record = svc.create_record(db, data)
    log_action(
        db, user_id=current_user.id, action="create", entity_type="timesheet_record",
        entity_id=record.id, new_data=data.model_dump(mode="json"),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return record


@router.put("/{record_id}", response_model=TimesheetRecordOut)
def update_record(
    record_id: int,
    data: TimesheetRecordUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    record = _get_record_or_404(db, record_id)
    old = {"status": record.status, "check_in": str(record.check_in), "check_out": str(record.check_out)}
    record = svc.update_record(db, record, data)
    log_action(
        db, user_id=current_user.id, action="update", entity_type="timesheet_record",
        entity_id=record_id, old_data=old, new_data=data.model_dump(exclude_unset=True, mode="json"),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return record


@router.post("/{record_id}/approve", response_model=TimesheetRecordOut)
def approve_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    record = _get_record_or_404(db, record_id)
    record = svc.approve_record(db, record, current_user.id)
    log_action(
        db, user_id=current_user.id, action="approve", entity_type="timesheet_record",
        entity_id=record_id, ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return record


@router.get("/summary/{user_id}", response_model=TimesheetSummary)
def get_summary(
    user_id: int,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    return svc.get_summary(db, user_id, year, month)
