from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from schemas.comment import CommentCreate, CommentResponse
from utils.auth_helpers import get_current_user, is_admin
from utils.db_helpers import (
    create_new_comment, get_comments_by_article, get_comment_by_id, delete_comment, get_article_by_id
)
from models.user import UserDB

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=CommentResponse)
def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authenticated users to comment on articles. """
    
    # Ensure the article exists
    article = get_article_by_id(db, comment.article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    new_comment = create_new_comment(db, comment, author_id=current_user.id)
    logger.info(f"User {current_user.id} commented on article '{article.title}' (ID: {comment.article_id})")
    
    return new_comment

@router.get("/{article_id}", response_model=List[CommentResponse])
def list_comments(
    article_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """ Retrieve comments for a specific article with pagination. """
    
    # Ensure valid pagination values
    limit = min(50, max(1, limit))  # Limit max results to 50
    
    # Ensure the article exists
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    comments = get_comments_by_article(db, article_id, skip, limit)
    logger.info(f"Fetched {len(comments)} comments for article '{article.title}' (ID: {article_id})")

    return comments

@router.delete("/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Allow authors of the article, comment owners, and admins to delete comments."""
    
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Ensure permission for deletion
    if comment.author_id == current_user.id or is_admin(current_user):
        delete_comment(db, comment_id)
        logger.info(f"User {current_user.id} deleted comment {comment_id} on article ID {comment.article_id}")
        return {"detail": f"Comment {comment_id} deleted successfully"}

    # Fetch article only if needed
    article = get_article_by_id(db, comment.article_id)
    if article and article.author_id == current_user.id:
        delete_comment(db, comment_id)
        logger.info(f"Article author {current_user.id} deleted comment {comment_id} on their article '{article.title}'")
        return {"detail": f"Comment {comment_id} deleted successfully"}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this comment")
