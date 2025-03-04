from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserDB, UserRole
from schemas import PromoteUserRequest
from auth import get_current_user

router = APIRouter()

@router.put("/admin/promote", response_model=dict)
def promote_user(
    request: PromoteUserRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # Ensure only Super Admins can promote users
    if current_user.role != UserRole.super_admin:
        raise HTTPException(status_code=403, detail="Only Super Admins can promote users.")

    # Find the target user
    user = db.query(UserDB).filter(UserDB.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Prevent demoting Super Admins
    if user.role == UserRole.super_admin and request.new_role != UserRole.super_admin:
        raise HTTPException(status_code=403, detail="Cannot demote a Super Admin.")

    # Update role
    user.role = request.new_role
    db.commit()
    db.refresh(user)

    return {"message": f"User {user.username} promoted to {user.role.value}."}
