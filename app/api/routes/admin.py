from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.session import get_db
from app.schemas.article import ArticleResponse
from app.schemas.comment import CommentResponse
from app.models.enums import UserRole
from app.models.refresh_token import RefreshTokenDB
from app.schemas.user import UserResponse, PromoteUserRequest
from app.api.deps import require_admin, require_super_admin
from app.services import (
    get_all_users, promote_user, delete_article, delete_comment,
    get_articles, get_all_comments, get_article_by_id, get_comment_by_id,
    get_user_by_id, update_user_role, delete_user_from_db
)
from app.models.user import UserDB
from app.schemas.token import RefreshTokenResponse

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_super_admin)
):
    """ Super admins can view all users. """
    users = get_all_users(db)
    logger.info(f"Super Admin {current_user.id} retrieved {len(users)} users.")
    return users

@router.post("/promote/{user_id}")
def promote_to_admin(
    user_id: int,
    role: str,  # Expecting "admin" or "super_admin"
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_super_admin)
):
    """ Super admins can promote users to admin or super admin. """
    new_role = UserRole.__members__.get(role.upper())
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Choose 'admin' or 'super_admin'."
        )

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role."
        )

    # Never silently demote an existing super admin through this endpoint.
    target = get_user_by_id(db, user_id)
    if target.role == UserRole.SUPER_ADMIN and new_role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admins cannot be demoted")

    promote_user(db, user_id, new_role)
    logger.info(f"Super Admin {current_user.id} promoted User {user_id} to {new_role.name}.")
    return {"detail": f"User {user_id} promoted to {new_role.name} successfully."}

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int,
    request: PromoteUserRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_super_admin)
):
    """Allow only Super Admins to change user roles."""
    db_user = get_user_by_id(db, user_id)

    role_str = request.new_role.value.upper()  # Ensure correct case handling
    if role_str not in UserRole.__members__:
        logger.error(f"Invalid role: {role_str}")
        raise HTTPException(status_code=400, detail="Invalid role")

    # Prevent Super Admin demotion & self-promotion
    if db_user.role == UserRole.SUPER_ADMIN and role_str != "SUPER_ADMIN":
        logger.warning(f"Attempted to demote super admin {db_user.username}")
        raise HTTPException(status_code=403, detail="Super Admins cannot be demoted")

    if db_user.id == current_user.id and role_str != "SUPER_ADMIN":
        logger.warning(f"User {current_user.username} attempted to change their own role")
        raise HTTPException(status_code=403, detail="You cannot change your own role")

    updated_user = update_user_role(db, current_user, user_id, role_str)

    logger.info(f"User {updated_user.username} role updated to {updated_user.role.value}")
    return {"detail": f"User {updated_user.username} role updated to {updated_user.role.value}"}


@router.get("/articles", response_model=List[ArticleResponse])
def list_all_articles(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Admins can view all articles regardless of status. """
    articles = get_articles(db, status=None, include_unlisted=True, limit=200)
    logger.info(f"Admin {current_user.id} retrieved {len(articles)} articles.")
    return articles

@router.delete("/articles/{article_id}")
def remove_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Admins can delete any article. """
    article = get_article_by_id(db, article_id)
    delete_article(db, article_id)
    logger.info(f"Admin {current_user.id} deleted article '{article.title}' (ID: {article_id}).")
    return {"detail": f"Article '{article.title}' deleted successfully."}

@router.get("/comments", response_model=List[CommentResponse])
def list_all_comments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Admins can view all comments. """
    comments = get_all_comments(db)
    logger.info(f"Admin {current_user.id} retrieved {len(comments)} comments.")
    return comments

@router.delete("/comments/{comment_id}")
def remove_comment_admin(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Allow only admins and super admins to delete any comment. """
    comment = get_comment_by_id(db, comment_id)
    delete_comment(db, comment_id)
    logger.info(f"Admin {current_user.id} deleted comment '{comment.content[:30]}...' (ID: {comment_id}).")
    return {"detail": f"Comment '{comment.content[:30]}...' deleted successfully."}

@router.get("/active-sessions", response_model=List[RefreshTokenResponse])
def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Admins can view active user sessions """
    sessions = db.query(RefreshTokenDB).filter(RefreshTokenDB.is_active == True).all()
    return sessions

@router.delete("/revoke/{token_id}")
def revoke_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    """ Admins can revoke user sessions """
    token = db.query(RefreshTokenDB).filter_by(id=token_id).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    token.is_active = False
    token.revoked = True
    db.commit()
    return {"detail": "Token revoked successfully"}

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_super_admin)
):
    """Allow only Super Admins to delete users."""
    db_user = get_user_by_id(db, user_id)

    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")

    delete_user_from_db(db, user_id)
    logger.info(f"User {db_user.username} deleted successfully")
    return {"detail": f"User {db_user.username} deleted successfully"}


@router.put("/verify/{user_id}")
def toggle_verified(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_super_admin)
):
    """Toggle a user's verified-writer badge (super admins only)."""
    db_user = get_user_by_id(db, user_id)
    db_user.is_verified = not db_user.is_verified
    db.commit()
    return {"detail": f"User {db_user.username} verified={db_user.is_verified}", "is_verified": db_user.is_verified}
