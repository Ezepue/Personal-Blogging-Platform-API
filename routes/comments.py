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
from utils.notification_helper import send_notification_to_user
from models.user import UserDB
from models.article import ArticleDB

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=CommentResponse)
async def add_comment(
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

    try:
        if article.author_id != current_user.id:
            await send_notification_to_user(
                db=db,
                user_id=article.author_id,
                message=f"{current_user.username} commented on \"{article.title}\"",
            )
    except Exception:
        pass  # notification failure must not fail the comment operation

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
    """Allow the comment owner, the article's author, and admins to delete a comment."""

    comment = get_comment_by_id(db, comment_id)

    is_owner = comment.user_id == current_user.id
    article = db.query(ArticleDB).filter(ArticleDB.id == comment.article_id).first()
    is_article_author = article is not None and article.author_id == current_user.id

    if not (is_owner or is_article_author or is_admin(current_user)):
        logger.warning(f"User {current_user.id} attempted to delete comment {comment_id} without permission.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    delete_comment(db, comment_id)
    logger.info(f"User {current_user.id} deleted comment {comment_id} on article ID {comment.article_id}")
    return {"status": "success", "detail": f"Comment {comment_id} deleted successfully"}
