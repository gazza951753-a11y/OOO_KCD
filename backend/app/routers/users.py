from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_user, require_hr, require_superadmin
from app.core.security import hash_password
from app.database import get_db
from app.models.user import Department, User, UserRole
from app.schemas.user import DepartmentCreate, DepartmentOut, DepartmentUpdate, UserCreate, UserOut, UserUpdate

router = APIRouter(tags=["users"])


# ── Departments ──────────────────────────────────────────────────────────────

@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_hr),
):
    return db.query(Department).all()


@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    dept = Department(**data.model_dump())
    db.add(dept)
    db.flush()
    log_action(db, user_id=current_user.id, action="create", entity_type="department", entity_id=dept.id,
               new_data=data.model_dump(), ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(404, "Отдел не найден")
    old = {"name": dept.name, "manager_id": dept.manager_id}
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    log_action(db, user_id=current_user.id, action="update", entity_type="department", entity_id=dept_id,
               old_data=old, new_data=data.model_dump(exclude_unset=True),
               ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(dept)
    return dept


# ── Users ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Пользователь с таким email уже существует")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        department_id=data.department_id,
        position=data.position,
    )
    db.add(user)
    db.flush()
    log_action(db, user_id=current_user.id, action="create", entity_type="user", entity_id=user.id,
               new_data={"email": data.email, "role": data.role},
               ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # employees can only view themselves
    if current_user.role == UserRole.employee and current_user.id != user_id:
        raise HTTPException(403, "Недостаточно прав")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    old = {"email": user.email, "role": user.role, "is_active": user.is_active}
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "password" and v:
            user.hashed_password = hash_password(v)
        else:
            setattr(user, k, v)
    log_action(db, user_id=current_user.id, action="update", entity_type="user", entity_id=user_id,
               old_data=old, new_data=data.model_dump(exclude_unset=True, exclude={"password"}),
               ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(400, "Нельзя деактивировать собственный аккаунт")
    user.is_active = False
    log_action(db, user_id=current_user.id, action="deactivate", entity_type="user", entity_id=user_id,
               ip_address=request.client.host if request.client else None)
    db.commit()
