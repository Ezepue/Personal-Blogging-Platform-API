from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update
from models.article import ArticleDB
from models.like import LikeDB
from database import get_db
from schemas.like import LikeResponse
from utils.auth_helpers import get_current_user
from models.user import UserDB
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{article_id}", response_model=LikeResponse)
def like_article(
    article_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """Like an article (if not already liked)."""

    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    existing_like = db.query(LikeDB).filter(
        LikeDB.article_id == article_id, 
        LikeDB.user_id == user.id
    ).one_or_none()
    
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already liked this article")

    # Add new like
    new_like = LikeDB(article_id=article_id, user_id=user.id)

    try:
        db.add(new_like)
        db.execute(update(ArticleDB).where(ArticleDB.id == article_id).values(likes_count=ArticleDB.likes_count + 1))
        db.commit()
        db.refresh(article)  # Refresh to get updated like count

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Like processing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing like")

    return LikeResponse(article_id=article.id, likes_count=article.likes_count, user_id=user.id)


@router.delete("/{article_id}", response_model=LikeResponse)
def unlike_article(
    article_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """Unlike an article (if previously liked)."""

    like = db.query(LikeDB).filter(
        LikeDB.article_id == article_id, 
        LikeDB.user_id == user.id
    ).one_or_none()

    if not like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not liked this article")

    try:
        db.delete(like)
        db.execute(update(ArticleDB).where(ArticleDB.id == article_id).values(likes_count=ArticleDB.likes_count - 1))
        db.commit()

        # Get the updated like count
        updated_likes = db.query(ArticleDB.likes_count).filter(ArticleDB.id == article_id).scalar()

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Unlike processing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing unlike")

    return LikeResponse(article_id=article_id, likes_count=updated_likes, user_id=user.id)


@router.get("/{article_id}/count", response_model=LikeResponse)
def get_like_count(article_id: int, db: Session = Depends(get_db)):
    """Get the like count for an article."""

    likes_count = db.query(ArticleDB.likes_count).filter(ArticleDB.id == article_id).scalar()
    if likes_count is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    return LikeResponse(article_id=article_id, likes_count=likes_count)
