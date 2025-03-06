from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.article import ArticleDB
from models.like import LikeDB
from database import get_db
from schemas.like import LikeResponse
from utils.auth_helpers import get_current_user

router = APIRouter()

@router.post("/{article_id}", response_model=LikeResponse)
def like_article(article_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Like an article (if not already liked)."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if user already liked this article
    existing_like = db.query(LikeDB).filter(LikeDB.article_id == article_id, LikeDB.user_id == user.id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this article")

    # Add new like
    new_like = LikeDB(article_id=article_id, user_id=user.id)

    db.add(new_like)
    article.likes_count += 1  # Update like count
    db.commit()
    db.refresh(article)
    
    return {"article_id": article.id, "likes_count": article.likes_count, "user_id": user.id}


@router.delete("/{article_id}", response_model=LikeResponse)
def unlike_article(article_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Unlike an article (if previously liked)."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Find and delete the like
    like = db.query(LikeDB).filter(LikeDB.article_id == article_id, LikeDB.user_id == user.id).first()

    if not like:
        raise HTTPException(status_code=400, detail="You have not liked this article")

    db.delete(like)
    article.likes_count -= 1  # Update like count
    db.commit()
    db.refresh(article)

    return {"article_id": article.id, "likes_count": article.likes_count, "user_id": user.id}

@router.get("/{article_id}/count")
def get_like_count(article_id: int, db: Session = Depends(get_db)):
    """Get the like count for an article."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {"article_id": article_id, "likes_count": article.likes_count}
