from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import require_manager
from app.database import get_db
from app.models.user import User
from app.services.reports import generate_timesheet_excel, generate_timesheet_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/timesheet/excel")
def timesheet_excel(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    department_id: int | None = Query(None),
    user_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    from app.models.user import UserRole
    if current_user.role == UserRole.manager:
        department_id = current_user.department_id

    data = generate_timesheet_excel(db, year, month, department_id, user_id)
    filename = f"timesheet_{year}_{month:02d}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/timesheet/pdf")
def timesheet_pdf(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    department_id: int | None = Query(None),
    user_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    from app.models.user import UserRole
    if current_user.role == UserRole.manager:
        department_id = current_user.department_id

    data = generate_timesheet_pdf(db, year, month, department_id, user_id)
    filename = f"timesheet_{year}_{month:02d}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/me/timesheet/excel")
def my_timesheet_excel(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    data = generate_timesheet_excel(db, year, month, user_id=current_user.id)
    filename = f"my_timesheet_{year}_{month:02d}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
