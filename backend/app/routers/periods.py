from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import require_hr, require_superadmin
from app.database import get_db
from app.models.period import TimesheetPeriod
from app.models.user import User

router = APIRouter(prefix="/periods", tags=["periods"])


class PeriodOut(BaseModel):
    id: int
    year: int
    month: int
    is_closed: bool
    closed_at: datetime | None
    closed_by: int | None

    model_config = {"from_attributes": True}


def _get_or_create(db: Session, year: int, month: int) -> TimesheetPeriod:
    period = db.query(TimesheetPeriod).filter(
        TimesheetPeriod.year == year,
        TimesheetPeriod.month == month,
    ).first()
    if not period:
        period = TimesheetPeriod(year=year, month=month)
        db.add(period)
        db.flush()
    return period


@router.get("", response_model=list[PeriodOut])
def list_periods(
    db: Session = Depends(get_db),
    _: User = Depends(require_hr),
):
    return (
        db.query(TimesheetPeriod)
        .order_by(TimesheetPeriod.year.desc(), TimesheetPeriod.month.desc())
        .all()
    )


@router.post("/{year}/{month}/close", response_model=PeriodOut)
def close_period(
    year: int,
    month: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    if not (1 <= month <= 12):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Неверный месяц")
    period = _get_or_create(db, year, month)
    if period.is_closed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Период уже закрыт")
    period.is_closed = True
    period.closed_at = datetime.now(timezone.utc)
    period.closed_by = current_user.id
    log_action(
        db,
        user_id=current_user.id,
        action="close_period",
        entity_type="timesheet_period",
        entity_id=period.id,
        new_data={"year": year, "month": month},
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(period)
    return period


@router.post("/{year}/{month}/open", response_model=PeriodOut)
def open_period(
    year: int,
    month: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    if not (1 <= month <= 12):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Неверный месяц")
    period = _get_or_create(db, year, month)
    if not period.is_closed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Период уже открыт")
    period.is_closed = False
    period.closed_at = None
    period.closed_by = None
    log_action(
        db,
        user_id=current_user.id,
        action="open_period",
        entity_type="timesheet_period",
        entity_id=period.id,
        new_data={"year": year, "month": month},
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(period)
    return period
