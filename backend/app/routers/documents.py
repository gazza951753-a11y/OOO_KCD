from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_user, require_hr, require_manager
from app.database import get_db
from app.models.document import DocumentRequest, DocumentStatus
from app.models.user import User, UserRole
from app.schemas.document import DocumentReject, DocumentRequestCreate, DocumentRequestOut
from app.services import documents as svc

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_doc_or_404(db: Session, doc_id: int) -> DocumentRequest:
    doc = db.query(DocumentRequest).filter(DocumentRequest.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Документ не найден")
    return doc


@router.get("", response_model=list[DocumentRequestOut])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    q = db.query(DocumentRequest)
    if current_user.role == UserRole.manager:
        # managers see requests from their department employees
        q = q.join(User, DocumentRequest.requester_id == User.id).filter(
            User.department_id == current_user.department_id
        )
    return q.order_by(DocumentRequest.created_at.desc()).all()


@router.get("/me", response_model=list[DocumentRequestOut])
def list_mine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(DocumentRequest)
        .filter(DocumentRequest.requester_id == current_user.id)
        .order_by(DocumentRequest.created_at.desc())
        .all()
    )


@router.post("", response_model=DocumentRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    data: DocumentRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = svc.create_request(db, data, current_user.id)
    log_action(
        db, user_id=current_user.id, action="create", entity_type="document_request",
        entity_id=doc.id, new_data=data.model_dump(),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return doc


@router.get("/{doc_id}", response_model=DocumentRequestOut)
def get_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_doc_or_404(db, doc_id)
    if current_user.role == UserRole.employee and doc.requester_id != current_user.id:
        raise HTTPException(403, "Недостаточно прав")
    return doc


@router.put("/{doc_id}/approve", response_model=DocumentRequestOut)
def approve(
    doc_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    doc = _get_doc_or_404(db, doc_id)
    if doc.status not in (DocumentStatus.pending, DocumentStatus.draft):
        raise HTTPException(400, "Документ уже обработан")
    doc = svc.approve_request(db, doc, current_user.id)
    log_action(
        db, user_id=current_user.id, action="approve", entity_type="document_request",
        entity_id=doc_id, ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return doc


@router.put("/{doc_id}/reject", response_model=DocumentRequestOut)
def reject(
    doc_id: int,
    data: DocumentReject,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    doc = _get_doc_or_404(db, doc_id)
    if doc.status not in (DocumentStatus.pending, DocumentStatus.draft):
        raise HTTPException(400, "Документ уже обработан")
    doc = svc.reject_request(db, doc, current_user.id, data.rejection_reason)
    log_action(
        db, user_id=current_user.id, action="reject", entity_type="document_request",
        entity_id=doc_id, new_data={"reason": data.rejection_reason},
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return doc
