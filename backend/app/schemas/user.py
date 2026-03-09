from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    manager_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    manager_id: int | None = None


class DepartmentOut(DepartmentBase):
    id: int
    manager_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.employee
    department_id: int | None = None
    position: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None
    department_id: int | None = None
    position: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    department: DepartmentOut | None = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str
