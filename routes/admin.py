from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.article import ArticleResponse
from schemas.comment import CommentResponse
from models.enums import UserRole
from schemas.user import UserResponse
from utils.auth_helpers import get_current_user, is_admin, is_super_admin
from utils.db_helpers import (
    get_all_users, promote_user, delete_article, delete_comment, 
    get_all_articles, get_all_comments
)
from models.user import UserDB

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Super admins can view all users. """
    if not is_super_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted to super admins.")
    
    return get_all_users(db)

@router.post("/promote/{user_id}")
def promote_to_admin(
    user_id: int,
    role: str,  # Expecting "admin" or "super_admin"
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Super admins can promote users to admin or super admin. """
    if not is_super_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted to super admins.")
    
    if role not in UserRole.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role.")

    return promote_user(db, user_id, UserRole[role])

@router.get("/articles", response_model=List[ArticleResponse])
def list_all_articles(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can view all articles. """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")

    return get_all_articles(db)

@router.delete("/articles/{article_id}")
def remove_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can delete any article. """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")

    delete_article(db, article_id)
    return {"detail": "Article deleted successfully"}

@router.get("/comments", response_model=List[CommentResponse])
def list_all_comments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can view all comments. """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")

    return get_all_comments(db)

@router.delete("/comments/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Admins can delete any comment. """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")

    delete_comment(db, comment_id)
    return {"detail": "Comment deleted successfully"}
