"""Request-scoped dependencies: the authorization surface routers depend on.

Routers import identity from here (interface segregation: each route asks for
exactly the guarantee it needs — a user, maybe-a-user, an admin, a super
admin) and never touch token internals directly.
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (  # noqa: F401  (re-exported for routers)
    create_access_token,
    create_preview_token,
    create_refresh_token,
    create_ws_ticket,
    hash_password,
    verify_access_token,
    verify_password,
    verify_preview_token,
    verify_refresh_token,
    verify_user_credentials,
)
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import UserDB

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="users/login", auto_error=False)

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token or expired",
    headers={"WWW-Authenticate": "Bearer"},
)


def _resolve_user(token: str, db: Session) -> Optional[UserDB]:
    """Decode an access token and load its active user, or return None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(UserDB).filter(UserDB.id == int(user_id)).first()
    except (JWTError, ValueError):
        return None
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserDB:
    """Require a valid access token; yield its active user or raise 401."""
    user = _resolve_user(token, db)
    if user is None:
        raise _credentials_exception
    return user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """Yield the authenticated user when credentials are present and valid, else None.

    Used by public endpoints whose response varies for signed-in viewers.
    Never raises on missing or invalid credentials.
    """
    if not token:
        return None
    return _resolve_user(token, db)


def is_admin(user: UserDB) -> bool:
    """Predicate: the user holds the admin or super-admin role."""
    return user.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}


def is_super_admin(user: UserDB) -> bool:
    """Predicate: the user holds the super-admin role."""
    return user.role == UserRole.SUPER_ADMIN


def require_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Admit only admins and super admins; raise 403 otherwise."""
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_super_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Admit only super admins; raise 403 otherwise."""
    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required"
        )
    return current_user
