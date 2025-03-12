from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from schemas.article import ArticleResponse
from schemas.comment import CommentResponse
from models.enums import UserRole
from models.refresh_token import RefreshTokenDB
from schemas.user import UserResponse, PromoteUserRequest
from utils.auth_helpers import get_current_user, is_admin, is_super_admin
from utils.db_helpers import (
    get_all_users, promote_user, delete_article, delete_comment, 
    get_articles, get_all_comments, get_article_by_id, get_comment_by_id,
    get_user_by_id, update_user_role
)
from models.user import UserDB
from schemas.token import RefreshTokenResponse  # Assuming you have this schema

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Super admins can view all users. """
    is_super_admin(current_user)  # This will raise HTTPException if unauthorized

    users = get_all_users(db)
    logger.info(f"Super Admin {current_user.id} retrieved {len(users)} users.")
    return users

@router.post("/promote/{user_id}")
def promote_to_admin(
    user_id: int,
    role: str,  # Expecting "admin" or "super_admin"
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Super admins can promote users to admin or super admin. """
    is_super_admin(current_user)  # Raise HTTPException if not super admin

    # Validate role
    new_role = UserRole.__members__.get(role.upper())
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Choose 'admin' or 'super_admin'."
        )

    # Prevent promoting a super admin to another super admin
    if new_role == UserRole.SUPER_ADMIN and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A super admin cannot promote themselves."
        )

    promote_user(db, user_id, new_role)
    logger.info(f"Super Admin {current_user.id} promoted User {user_id} to {new_role.name}.")
    return {"detail": f"User {user_id} promoted to {new_role.name} successfully."}

@router.put("/{user_id}/role")
def change_user_role(
    user_id: int, 
    request: PromoteUserRequest,  
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    """Allow only Super Admins to change user roles."""
    if not is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action.")

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

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
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can view all articles. """
    is_admin(current_user)  # This will raise HTTPException if unauthorized

    articles = get_articles(db)
    logger.info(f"Admin {current_user.id} retrieved {len(articles)} articles.")
    return articles

@router.delete("/articles/{article_id}")
def remove_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can delete any article. """
    is_admin(current_user)  # This will raise HTTPException if unauthorized

    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    delete_article(db, article_id)
    logger.info(f"Admin {current_user.id} deleted article '{article.title}' (ID: {article_id}).")
    return {"detail": f"Article '{article.title}' deleted successfully."}

@router.get("/comments", response_model=List[CommentResponse])
def list_all_comments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can view all comments. """
    is_admin(current_user)  # This will raise HTTPException if unauthorized

    comments = get_all_comments(db)
    logger.info(f"Admin {current_user.id} retrieved {len(comments)} comments.")
    return comments

@router.delete("/comments/{comment_id}")
def remove_comment_admin(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow only admins and super admins to delete any comment. """
    is_admin(current_user)  # Ensures only admins/super admins can delete

    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    delete_comment(db, comment_id, current_user, allow_admin=True)
    logger.info(f"Admin {current_user.id} deleted comment '{comment.content[:30]}...' (ID: {comment_id}).")
    return {"detail": f"Comment '{comment.content[:30]}...' deleted successfully."}

@router.get("/active-sessions", response_model=List[RefreshTokenResponse])
def get_active_sessions(
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can view active user sessions """
    is_admin(current_user)

    sessions = db.query(RefreshTokenDB).filter(RefreshTokenDB.is_active == True).all()
    return sessions

@router.delete("/revoke/{token_id}")
def revoke_token(
    token_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can revoke user sessions """
    is_admin(current_user)

    token = db.query(RefreshTokenDB).filter_by(id=token_id).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    token.is_active = False
    db.commit()
    return {"detail": "Token revoked successfully"}
