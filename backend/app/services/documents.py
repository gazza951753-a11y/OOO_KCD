from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.document import DocumentRequest, DocumentStatus
from app.schemas.document import DocumentRequestCreate


def create_request(db: Session, data: DocumentRequestCreate, requester_id: int) -> DocumentRequest:
    doc = DocumentRequest(**data.model_dump(), requester_id=requester_id, status=DocumentStatus.pending)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def approve_request(db: Session, doc: DocumentRequest, approver_id: int) -> DocumentRequest:
    doc.status = DocumentStatus.approved
    doc.approver_id = approver_id
    doc.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)
    return doc


def reject_request(
    db: Session, doc: DocumentRequest, approver_id: int, reason: str
) -> DocumentRequest:
    doc.status = DocumentStatus.rejected
    doc.approver_id = approver_id
    doc.approved_at = datetime.now(timezone.utc)
    doc.rejection_reason = reason
    db.commit()
    db.refresh(doc)
    return doc
