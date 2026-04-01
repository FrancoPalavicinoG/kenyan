import logging

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created user id=%d email=%s", user.id, user.email)
    return user


def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ValueError("User not found")
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    for field in payload.model_fields_set:
        setattr(user, field, getattr(payload, field))
    db.commit()
    db.refresh(user)
    logger.info("Updated user id=%d fields=%s", user_id, payload.model_fields_set)
    return user
