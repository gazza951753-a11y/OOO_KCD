from datetime import datetime

from pydantic import BaseModel

from app.models.document import DocumentStatus, DocumentType
from app.schemas.user import UserOut


class DocumentRequestBase(BaseModel):
    type: DocumentType
    title: str
    description: str | None = None


class DocumentRequestCreate(DocumentRequestBase):
    pass


class DocumentRequestUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class DocumentApprove(BaseModel):
    pass


class DocumentReject(BaseModel):
    rejection_reason: str


class DocumentRequestOut(DocumentRequestBase):
    id: int
    requester_id: int
    status: DocumentStatus
    approver_id: int | None
    approved_at: datetime | None
    rejection_reason: str | None
    file_path: str | None
    created_at: datetime
    updated_at: datetime
    requester: UserOut | None = None
    approver: UserOut | None = None

    model_config = {"from_attributes": True}


class DocumentTemplateBase(BaseModel):
    name: str
    type: DocumentType
    template_content: str


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateOut(DocumentTemplateBase):
    id: int
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
