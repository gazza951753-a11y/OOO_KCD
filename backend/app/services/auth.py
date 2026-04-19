from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def issue_tokens(user: User) -> dict:
    payload = {"sub": str(user.id), "role": str(user.role.value)}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
    }


def refresh_tokens(db: Session, refresh_token: str) -> dict | None:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        return None
    raw_sub = payload.get("sub")
    user_id = int(raw_sub) if raw_sub else None
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        return None
    return issue_tokens(user)
