from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from database import get_db
from schemas.user import UserCreate, UserResponse
from utils.auth_helpers import (
    create_access_token, get_current_user, hash_password,
    verify_user_credentials, is_super_admin, create_refresh_token,
    verify_refresh_token, revoke_refresh_token
)
from utils.db_helpers import (
    create_new_user, get_user_by_id, update_user_role, delete_user_from_db
)
from models.user import UserDB, UserRole
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """ Register a new user with default role 'reader'. """
    
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return create_new_user(db, user)

@router.post("/login/")
@limiter.limit("3/minute")
def login(
    request: Request,  
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ Authenticate user and return JWT access and refresh tokens. """
    user = verify_user_credentials(db, form_data.username, form_data.password)
    if user is None:
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """ Refresh access token using a valid refresh token. """
    user_id = verify_refresh_token(refresh_token, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": str(user_id)})
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    """Revoke a refresh token on logout."""
    revoke_refresh_token(refresh_token, db)
    return {"detail": "Logged out successfully"}

@router.get("/me/", response_model=UserResponse)
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    """ Get the current authenticated user's profile. """
    return current_user

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int, 
    new_role: dict,
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Allow only Super Admins to change user roles. """
    if not is_super_admin(user):
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action.")

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    role_str = new_role.get("role")
    if role_str not in UserRole.__members__:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Prevent Super Admin demotion & self-promotion
    if db_user.role == UserRole.super_admin and role_str != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admins cannot be demoted")

    if db_user.id == user.id and role_str != "super_admin":
        raise HTTPException(status_code=403, detail="You cannot change your own role")

    updated_user = update_user_role(db, user_id, UserRole[role_str.upper()])
    return {"detail": f"User {updated_user.username} role updated to {updated_user.role.value}"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)  
):
    """ Allow only Super Admins to delete users. """
    if not is_super_admin(user):
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action.")

    delete_user_from_db(db, user_id)
    return {"detail": "User deleted successfully"}
