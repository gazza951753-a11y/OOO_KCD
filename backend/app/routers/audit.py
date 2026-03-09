from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_hr, require_superadmin
from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    return q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[AuditLogOut])
def entity_audit(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_hr),
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
