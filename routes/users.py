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
    verify_user_credentials, is_super_admin
)
from utils.db_helpers import (
    create_new_user, get_user_by_id, update_user_role, delete_user_from_db
)
from models.user import UserDB, UserRole
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# Rate limiter for login
limiter = Limiter(key_func=get_remote_address)


@router.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """ Register a new user with default role 'reader'. """
    return create_new_user(db, user)


@router.post("/login/")
@limiter.limit("3/minute")  # Limits login attempts to prevent abuse
def login(
    request: Request,  
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ Authenticate user and return JWT access token. """
    user = verify_user_credentials(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Include user role in the JWT token for authorization
    access_token = create_access_token(
    {"sub": str(user.id), "role": user.role.value},  # Store user ID instead of username
    timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=UserResponse)
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    """ Get the current authenticated user's profile. """
    return current_user


@router.put("/{user_id}/role")
def change_user_role(
    user_id: int, 
    new_role: dict,  # Expecting JSON {"role": "admin"}
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Allow only Super Admins to change user roles. """
    is_super_admin(user)  # Ensures only Super Admins can modify roles

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    role_str = new_role.get("role", "").strip()
    if role_str not in UserRole.__members__:
        raise HTTPException(status_code=400, detail="Invalid role")

    updated_user = update_user_role(db, user_id, UserRole[role_str])
    return {"detail": f"User {updated_user.username} role updated to {updated_user.role.value}"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)  
):
    """ Allow only Super Admins to delete users. """
    is_super_admin(user)  # Authorization check

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user_from_db(db, user_id)
    return {"detail": "User deleted successfully"}


@router.post("/create-super-admin/", response_model=UserResponse)
def create_super_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    """ Create the first Super Admin if none exists. """

    existing_super_admin = db.query(UserDB).filter(UserDB.role == UserRole.super_admin.value).first()
    if existing_super_admin:
        raise HTTPException(status_code=403, detail="Super Admin already exists")

    new_user = create_new_user(
        db, 
        user_data, 
        role=UserRole.super_admin.value  # Explicitly setting role
    )
    return new_user
