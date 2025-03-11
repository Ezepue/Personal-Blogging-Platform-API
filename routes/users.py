import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from slowapi import Limiter
from slowapi.util import get_remote_address 

from database import get_db
from schemas.user import UserCreate, UserResponse
from utils.auth_helpers import (
    create_access_token, get_current_user, hash_password,
    verify_user_credentials, is_super_admin, create_refresh_token,
    revoke_refresh_token, verify_refresh_token
)
from utils.db_helpers import (
    create_new_user, get_user_by_id, update_user_role, delete_user_from_db
)
from models.user import UserDB, UserRole
from models.refresh_token import RefreshTokenDB  
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    # new_user = create_new_user(db, user.username, user.email, hashed_pw)
    new_user = create_new_user(db, user, role=UserRole.READER)

    
    logger.info(f"New user registered: {new_user.username} ({new_user.email})")
    return new_user

@router.post("/login")
@limiter.limit("3/minute")
def login(
    request: Request,  
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT access and refresh tokens."""
    
    user = verify_user_credentials(db, form_data.username, form_data.password)
    if user is None:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(user.id, db)

    logger.info(f"User {user.username} logged in successfully.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int, 
    new_role: dict,
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    """Allow only Super Admins to change user roles."""
    if not is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action.")

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    role_str = new_role.get("role", "").upper()
    if role_str not in UserRole.__members__:
        logger.error(f"Invalid role: {role_str}")
        raise HTTPException(status_code=400, detail="Invalid role")

    # Prevent Super Admin demotion & self-promotion
    if db_user.role == UserRole.SUPER_ADMIN and role_str != "SUPER_ADMIN":
        logger.warning(f"Attempted to demote super admin {db_user.username}")
        raise HTTPException(status_code=403, detail="Super Admins cannot be demoted")

    if db_user.id == current_user.id and role_str != "SUPER_ADMIN":
        logger.warning(f"User {current_user.username} attempted to change their own role")
        raise HTTPException(status_code=403, detail="You cannot change your own role")

    updated_user = update_user_role(db, user_id, UserRole[role_str])
    logger.info(f"User {updated_user.username} role updated to {updated_user.role.value}")
    return {"detail": f"User {updated_user.username} role updated to {updated_user.role.value}"}

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    user_id = verify_refresh_token(refresh_token, db)
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": str(user_id)})
    logger.info(f"Access token refreshed for user {user_id}")
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    """Logout by deactivating refresh tokens."""
    # Ensure the refresh tokens exist for the current user
    refresh_tokens = db.query(RefreshTokenDB).filter_by(user_id=current_user.id, is_active=True).all()
    
    if not refresh_tokens:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active refresh tokens found")
    
    # Deactivate the refresh tokens
    db.query(RefreshTokenDB).filter_by(user_id=current_user.id).update({"is_active": False})
    db.commit()
    
    return {"detail": "Logged out successfully"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)  
):
    """Allow only Super Admins to delete users."""
    if not is_super_admin(current_user):
        logger.warning(f"User {current_user.username} attempted to delete a user without proper permissions.")
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action.")

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    delete_user_from_db(db, user_id)
    logger.info(f"User {db_user.username} deleted successfully")
    return {"detail": f"User {db_user.username} deleted successfully"}
