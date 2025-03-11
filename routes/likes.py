from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, func
from models.article import ArticleDB
from models.like import LikeDB
from database import get_db
from schemas.like import LikeResponse
from utils.auth_helpers import get_current_user
from utils.db_helpers import get_article_with_likes
from models.user import UserDB
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/{article_id}", response_model=LikeResponse)
def like_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: UserDB = Depends(get_current_user)
):
    """Like an article (if not already liked)."""
    logger.info(f"User {user.id} attempting to like article {article_id}")

    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        logger.warning(f"Article {article_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    existing_like = db.query(LikeDB).filter(
        LikeDB.article_id == article_id,
        LikeDB.user_id == user.id
    ).first()

    if existing_like:
        logger.info(f"User {user.id} already liked article {article_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already liked this article")

    try:
        # Insert like
        new_like = LikeDB(article_id=article_id, user_id=user.id)
        db.add(new_like)
        db.commit()

        # Update likes_count using COUNT(*)
        likes_count = db.query(func.count(LikeDB.id)).filter(LikeDB.article_id == article_id).scalar()
        db.query(ArticleDB).filter(ArticleDB.id == article_id).update({"likes_count": likes_count})
        db.commit()

        logger.info(f"User {user.id} liked article {article_id}, new count: {likes_count}")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error processing like for article {article_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing like")

    return LikeResponse(
        message="Successfully liked the article.",
        user_id=user.id,
        article_id=article.id,
        likes_count=likes_count
    )

@router.delete("/{article_id}", response_model=LikeResponse)
def unlike_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: UserDB = Depends(get_current_user)
):
    """Unlike an article (if previously liked)."""
    logger.info(f"User {user.id} is trying to unlike article {article_id}")

    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        logger.warning(f"Article {article_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    like = db.query(LikeDB).filter(
        LikeDB.article_id == article_id,
        LikeDB.user_id == user.id
    ).one_or_none()

    if not like:
        logger.info(f"User {user.id} has not liked article {article_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not liked this article")

    try:
        # ✅ Delete the like
        db.delete(like)
        db.commit()

        # ✅ Update likes_count using COUNT(*)
        likes_count = db.query(func.count(LikeDB.id)).filter(LikeDB.article_id == article_id).scalar()
        db.query(ArticleDB).filter(ArticleDB.id == article_id).update({"likes_count": likes_count})
        db.commit()

        logger.info(f"User {user.id} unliked article {article_id}, new count: {likes_count}")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Unlike processing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing unlike")

    return LikeResponse(
        message="Successfully unliked the article.",
        user_id=user.id,
        article_id=article.id,
        likes_count=likes_count
    )


@router.get("/{article_id}/count", response_model=LikeResponse)
def get_like_count(article_id: int, db: Session = Depends(get_db)):
    """Get the like count for an article."""
    logger.info(f"Fetching like count for article {article_id}")

    likes_count = db.query(ArticleDB.likes_count).filter(ArticleDB.id == article_id).scalar()
    if likes_count is None:
        logger.warning(f"Article {article_id} not found when fetching like count")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    logger.info(f"Article {article_id} has {likes_count} likes")
    
    return LikeResponse(
        message="Like count retrieved successfully.",
        article_id=article_id,
        likes_count=likes_count,
        user_id=None  # Optional, since we're only fetching the count
    )
