from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import SecretStr
from typing import Optional
import logging
import os
import secrets
from dotenv import load_dotenv

from models.user import UserDB
from models.token import RefreshTokenDB
from models.enums import UserRole
from database import get_db
from config import SECRET_KEY, ALGORITHM

# Load environment variables
load_dotenv()

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Security Utilities
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", scopes={"admin": "Admin privileges"})
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logging setup
logger = logging.getLogger(__name__)

def hash_password(password: SecretStr) -> str:
    """Securely hash a password."""
    return pwd_context.hash(password.get_secret_value())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int, db: Session) -> str:
    """Generate a refresh token and store it in the database."""
    refresh_token = secrets.token_urlsafe(64)  # More secure than JWT for refresh
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshTokenDB(user_id=user_id, token=refresh_token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return refresh_token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserDB:
    """Decode JWT token and retrieve the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        user = db.query(UserDB).filter(UserDB.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

def revoke_refresh_token(token: str, db: Session):
    """Revoke a refresh token."""
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == token).first()
    if db_token:
        db_token.revoked = True
        db.commit()

def refresh_access_token(db: Session, refresh_token: str) -> str:
    """Validate refresh token and issue a new access token."""
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == refresh_token).first()
    
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    return create_access_token({"sub": str(db_token.user_id)})

def verify_refresh_token(token: str, db: Session) -> int:
    """Verify a refresh token and return the user ID."""
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == token).first()
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    return db_token.user_id

def delete_expired_tokens(db: Session):
    """Remove expired refresh tokens from the database."""
    db.query(RefreshTokenDB).filter(RefreshTokenDB.expires_at < datetime.utcnow()).delete()
    db.commit()


import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import UserDB
from models.token import RefreshToken
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(db: Session, user_id: int):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    refresh_token = RefreshToken(user_id=user_id, token=token, expires_at=expire, is_active=True)
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return token

def is_admin(user: UserDB):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return True

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Retrieve the current logged-in user from the access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(UserDB).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
