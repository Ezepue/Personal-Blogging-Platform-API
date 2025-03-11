from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.token import TokenResponse
from utils.auth_helpers import authenticate_user, create_access_token, create_refresh_token, get_current_user
from models.user import UserDB
from models.refresh_token import RefreshTokenDB  

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate access and refresh tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


