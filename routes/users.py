from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from schemas import UserCreate, UserResponse
from database import get_db
from crud import create_user
from auth import authenticate_user, create_access_token, get_current_user, hash_password, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from models import UserDB, UserRole

router = APIRouter()

# ✅ Define a local rate limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """ Register a new user with default role 'reader'. """
    return create_user(db, user)

@router.post("/login/")
@limiter.limit("3/minute")
def login(
    request: Request,  # ✅ Added request parameter
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ Authenticate user and return JWT access token. """
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Include user role in the JWT token
    access_token = create_access_token(
        {"sub": user.username, "role": user.role.value},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me/", response_model=UserResponse)
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    """ Get the current authenticated user. """
    return current_user

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int, 
    new_role: dict,  # Expecting JSON {"role": "admin"}
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Only Super Admin can change user roles. """
    if user.role != UserRole.super_admin:
        raise HTTPException(status_code=403, detail="Only Super Admin can change user roles")

    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    role_str = new_role.get("role")  # Prevent KeyError if "role" is missing
    if role_str not in UserRole.__members__:
        raise HTTPException(status_code=400, detail="Invalid role")

    db_user.role = UserRole[role_str]  # Convert string to Enum safely
    db.commit()
    db.refresh(db_user)
    return {"detail": f"User {db_user.username} role updated to {db_user.role.value}"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)  
):
    """ Only Super Admin can delete users. """
    if user.role != UserRole.super_admin:
        raise HTTPException(status_code=403, detail="Only Super Admin can delete users")

    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

@router.post("/create-super-admin/", response_model=UserResponse)
def create_super_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    """ Create the first Super Admin if none exists. """

    existing_super_admin = db.query(UserDB).filter(UserDB.role == UserRole.super_admin.value).first()
    
    if existing_super_admin:
        raise HTTPException(status_code=403, detail="Super Admin already exists")

    new_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),  # Hash password
        role=UserRole.super_admin.value  # Assign Super Admin role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
