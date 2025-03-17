import logging
import os
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import SecretStr

from models.user import UserDB
from models.refresh_token import RefreshTokenDB
from models.enums import UserRole
from database import get_db
from config import SECRET_KEY, ALGORITHM

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Security Utilities
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", scopes={"admin": "Admin privileges"})
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Password Hashing & Verification
def hash_password(password: SecretStr) -> str:
    return pwd_context.hash(password.get_secret_value())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

# JWT Token Creation & Verification
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": "access"})

    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Generated access token for user {data['sub']} with expiration {expire}")
    return encoded_token

def verify_access_token(token: str) -> Optional[dict]:
    """Verify and decode the JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "exp" in payload and datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        return payload  # The decoded token data (contains user info)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def create_refresh_token(user_id: int, db: Session) -> str:
    try:
        refresh_token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        db_token = RefreshTokenDB(user_id=user_id, token=refresh_token, expires_at=expires_at)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)

        logger.info(f"Generated refresh token for user {user_id} with expiration {expires_at}")
        return refresh_token
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

def verify_refresh_token(refresh_token: str, db: Session) -> Optional[int]:
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == refresh_token).first()
    if not db_token:
        logger.warning("Refresh token not found.")
        return None
    if db_token.revoked:
        logger.info(f"Refresh token {refresh_token} has been revoked.")
        return None
    if db_token.expires_at < datetime.utcnow():
        logger.info(f"Refresh token {refresh_token} expired at {db_token.expires_at}.")
        return None
    return db_token.user_id

# Token Validation and User Retrieval
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token required")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing 'sub' field.")
            raise credentials_exception
        user = db.query(UserDB).filter(UserDB.id == int(user_id)).first()
        if user is None:
            logger.warning(f"Authentication failed: User {user_id} not found")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT decoding failed: {e}")
        raise credentials_exception

    logger.info(f"User {user.username} authenticated successfully")
    return user

def verify_user_credentials(db: Session, username: str, password: str) -> Optional[UserDB]:
    """Verify user credentials against the database."""
    user = db.query(UserDB).filter(UserDB.username.ilike(username)).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Revoke Refresh Token
def revoke_refresh_token(token: str, db: Session):
    try:
        db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == token).first()
        if not db_token:
            logger.warning(f"Attempted to revoke non-existing token {token}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token not found")
        if db_token.revoked:
            logger.info(f"Refresh token {token} already revoked")
            return
        db_token.revoked = True
        db_token.is_active = False
        db.commit()
        logger.info(f"Revoked refresh token {token} for user {db_token.user_id}")
    except Exception as e:
        logger.error(f"Error revoking refresh token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Refresh Access Token
def refresh_access_token(db: Session, refresh_token: str) -> str:
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == refresh_token).first()
    if not db_token:
        logger.warning("Refresh token not found in database")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if db_token.revoked:
        logger.info(f"Revoked token attempted: {refresh_token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
    if not db_token.is_active:
        logger.info(f"Inactive token attempted: {refresh_token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is inactive")
    if db_token.expires_at < datetime.utcnow():
        logger.info(f"Expired refresh token: {refresh_token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    return create_access_token({"sub": str(db_token.user_id)})

# Delete Expired Tokens
def delete_expired_tokens(db: Session):
    try:
        count = db.query(RefreshTokenDB).filter(RefreshTokenDB.expires_at < datetime.utcnow()).delete(synchronize_session=False)
        db.commit()
        logger.info(f"Deleted {count} expired tokens from the database")
    except Exception as e:
        logger.error(f"Error deleting expired tokens: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Role-based Access Control
def is_admin(user: UserDB):
    """Check if the user is an admin."""
    logger.info(f"Checking admin access for user {user.username}, role: {user.role}")

    if user.role not in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:  # Use Enum
        logger.warning(f"Access denied: User {user.username} (role: {user.role}) is not an admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    logger.info(f"User {user.username} granted admin access.")
    return True

def is_super_admin(user: UserDB):
    """Check if the user is a super admin."""
    logger.info(f"Checking super admin access for user {user.username}, role: {user.role}")

    if user.role != UserRole.SUPER_ADMIN:  # Use Enum comparison
        logger.warning(f"Access denied: User {user.username} (role: {user.role}) is not a super admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )

    logger.info(f"User {user.username} granted super admin access.")
    return True

# Logging Configuration (to be called in main.py or the entry point)
logging.basicConfig(level=logging.INFO)
