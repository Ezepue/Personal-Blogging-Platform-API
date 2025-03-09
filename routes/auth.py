from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.token import TokenResponse
from utils.auth_helpers import authenticate_user, create_access_token, create_refresh_token
from models.user import UserDB

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(db, user.id)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    """Logout by deactivating refresh tokens."""
    db.query(RefreshToken).filter_by(user_id=current_user.id).update({"is_active": False})
    db.commit()
    return {"detail": "Logged out successfully"}
