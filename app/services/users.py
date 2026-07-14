"""User domain: account creation, profiles, roles, and soft deletion."""
import logging
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.article import ArticleDB
from app.models.comment import CommentDB
from app.models.enums import ArticleStatus, UserRole
from app.models.refresh_token import RefreshTokenDB
from app.models.user import UserDB
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

PROFILE_FIELDS = {"username", "email", "bio", "website", "location", "twitter", "github", "avatar_url"}


def get_user_by_id(db: Session, user_id: int) -> UserDB:
    """Fetch a user by id, raising 404 when absent."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_username(db: Session, username: str):
    """Fetch a user by exact username, or None."""
    return db.query(UserDB).filter(UserDB.username == username).first()


def create_new_user(db: Session, user_data: UserCreate, role: UserRole = UserRole.READER) -> UserDB:
    """Register a new account, enforcing unique username and email."""
    existing_user = db.query(UserDB).filter(
        or_(
            func.lower(UserDB.username) == user_data.username.lower(),
            func.lower(UserDB.email) == user_data.email.lower(),
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already taken")

    new_user = UserDB(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=hash_password(user_data.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created: {new_user.username} (ID: {new_user.id})")
    return new_user


def update_user_profile(db: Session, user: UserDB, data: dict) -> UserDB:
    """Apply whitelisted profile fields and persist."""
    for key, value in data.items():
        if key in PROFILE_FIELDS:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def update_user_role(db: Session, current_user: UserDB, user_id: int, new_role: str) -> UserDB:
    """Change another user's role, guarding self-change and super-admin demotion."""
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change your own role")

    user = get_user_by_id(db, user_id)
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Super Admins cannot be downgraded")
    if user.role == UserRole[new_role]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this role")

    user.role = UserRole[new_role]
    db.commit()
    db.refresh(user)
    return user


def promote_user(db: Session, user_id: int, new_role: UserRole) -> UserDB:
    """Assign a role to a user (super-admin operation)."""
    if not isinstance(new_role, UserRole):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def delete_user_from_db(db: Session, user_id: int) -> None:
    """Soft-delete an account: deactivate, hide content, revoke sessions."""
    user = get_user_by_id(db, user_id)
    user.is_active = False

    db.query(ArticleDB).filter(ArticleDB.author_id == user_id).update(
        {ArticleDB.status: ArticleStatus.DELETED}, synchronize_session=False
    )
    db.query(CommentDB).filter(CommentDB.user_id == user_id).update(
        {CommentDB.is_deleted: True}, synchronize_session=False
    )
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == user_id).update(
        {RefreshTokenDB.is_active: False, RefreshTokenDB.revoked: True},
        synchronize_session=False,
    )
    db.commit()
    logger.info(f"User {user.username} and associated content soft deleted.")


def get_all_users(db: Session) -> List[UserDB]:
    """All users, id-ordered (admin listing)."""
    return db.query(UserDB).order_by(UserDB.id).all()
