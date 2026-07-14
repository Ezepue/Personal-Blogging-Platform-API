from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from database import get_db
from models.bookmark import BookmarkDB
from models.article import ArticleDB
from models.user import UserDB
from models.enums import ArticleStatus
from schemas.article import ArticleResponse
from utils.auth_helpers import get_current_user
from utils.db_helpers import get_article_by_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ArticleResponse])
def list_bookmarks(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    """The user's reading list: bookmarked articles, most recently saved first."""
    limit = min(100, max(1, limit))
    rows = (
        db.query(ArticleDB)
        .join(BookmarkDB, BookmarkDB.article_id == ArticleDB.id)
        .filter(
            BookmarkDB.user_id == current_user.id,
            ArticleDB.status == ArticleStatus.PUBLISHED,
        )
        .order_by(BookmarkDB.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rows


@router.get("/{article_id}/status")
def bookmark_status(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Whether the current user has bookmarked this article."""
    bookmarked = (
        db.query(BookmarkDB)
        .filter(BookmarkDB.user_id == current_user.id, BookmarkDB.article_id == article_id)
        .first()
        is not None
    )
    return {"bookmarked": bookmarked}


@router.post("/{article_id}", status_code=status.HTTP_200_OK)
def add_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Save an article to the reading list."""
    get_article_by_id(db, article_id)  # 404 if missing
    try:
        db.add(BookmarkDB(user_id=current_user.id, article_id=article_id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Article already bookmarked")
    return {"detail": "Bookmarked", "bookmarked": True}


@router.delete("/{article_id}", status_code=status.HTTP_200_OK)
def remove_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Remove an article from the reading list."""
    bookmark = db.query(BookmarkDB).filter(
        BookmarkDB.user_id == current_user.id, BookmarkDB.article_id == article_id
    ).one_or_none()
    if bookmark is None:
        raise HTTPException(status_code=400, detail="Article is not bookmarked")
    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark removed", "bookmarked": False}
