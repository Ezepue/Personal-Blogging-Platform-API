import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from schemas.user import UserCreate, UserResponse, UserProfileUpdate, UserPasswordChange, UserPublicProfile
from utils.auth_helpers import (
    create_access_token, get_current_user, hash_password, verify_password,
    verify_user_credentials, create_refresh_token, verify_refresh_token
)
from utils.db_helpers import create_new_user, get_user_by_username, update_user_profile
from models.user import UserDB, UserRole
from models.refresh_token import RefreshTokenDB
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, UPLOAD_FOLDER

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

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

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    user_id = verify_refresh_token(refresh_token, db)
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(
        {"sub": str(user_id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"Access token refreshed for user {user_id}")
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    """Logout by deactivating refresh tokens."""
    try:
        refresh_tokens = db.query(RefreshTokenDB).filter_by(user_id=current_user.id, is_active=True).all()

        if not refresh_tokens:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active refresh tokens found")

        db.query(RefreshTokenDB).filter_by(user_id=current_user.id, is_active=True).update({"is_active": False})
        db.commit()

        return {"detail": "Logged out successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Logout failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.username and data.username != current_user.username:
        existing = get_user_by_username(db, data.username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")
    updated = update_user_profile(db, current_user, data.model_dump(exclude_none=True))
    return updated

@router.put("/me/password")
async def change_password(
    data: UserPasswordChange,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only image files are allowed for avatars")
    filename = f"avatar_{current_user.id}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    avatar_url = f"/media/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{username}/profile", response_model=UserPublicProfile)
async def get_public_profile(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
