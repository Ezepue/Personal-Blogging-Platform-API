from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import SecretStr
from typing import Optional

from models.user import UserDB
from models.enums import UserRole
from database import get_db
from config import SECRET_KEY, ALGORITHM

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security Utilities
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: SecretStr) -> str:
    """Securely hash a password."""
    return pwd_context.hash(password.get_secret_value())  # Extract secret value

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> UserDB:
    """Authenticate user credentials and return the user if valid."""
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserDB:
    """Decode JWT token and retrieve the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # Extract user ID
        if not user_id or not user_id.isdigit():  # Ensure it's a valid numeric ID
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Convert user_id to integer for database lookup
    user = db.query(UserDB).filter(UserDB.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

def verify_user_credentials(db: Session, username: str, password: str) -> Optional[UserDB]:
    """Authenticate user credentials and return the user if valid."""
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def is_admin(user: UserDB):
    """Ensure the user is an admin or super admin."""
    if user.role not in {UserRole.admin, UserRole.super_admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can perform this action"
        )
    return True

def is_super_admin(user: UserDB):
    """Ensure the user is a super admin."""
    if user.role != UserRole.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only super admins can perform this action"
        )
    return True
