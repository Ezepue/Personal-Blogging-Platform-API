from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import logging

from database import get_db
from config import FRONTEND_URL
from models.article import ArticleDB
from models.enums import ArticleStatus
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from utils.auth_helpers import get_current_user, is_admin
from utils.db_helpers import (
    create_new_article, get_article_by_id,
    update_article, delete_article, get_articles, get_user_drafts
)
from models.user import UserDB

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Create a new article. Only authenticated users can post. """
    # Ensure title and content are valid (Add custom validations if needed)
    if not article.title or len(article.title) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be at least 5 characters long."
        )
    if not article.content or len(article.content) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be at least 10 characters long."
        )

    new_article = create_new_article(db, article, author_id=current_user.id)
    logger.info(f"User {current_user.id} created article '{new_article.title}' (ID: {new_article.id})")
    return new_article

@router.get("", response_model=List[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    status: Optional[ArticleStatus] = ArticleStatus.PUBLISHED,
):
    """ Fetch articles. Defaults to PUBLISHED only; pass status=DRAFT to filter drafts. """

    # Restrict pagination limits
    limit = min(50, max(1, limit))

    articles = get_articles(db, search=search, category=category, skip=skip, limit=limit, status=status)

    logger.info(f"Fetched {len(articles)} articles (Search: '{search}', Category: '{category}', Status: '{status}').")

    return articles or []


@router.get("/my-drafts", response_model=List[ArticleResponse])
def list_my_drafts(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    """ Return all DRAFT articles belonging to the authenticated user. """
    is_author_or_above(current_user)
    limit = min(100, max(1, limit))
    drafts = get_user_drafts(db, author_id=current_user.id, skip=skip, limit=limit)
    logger.info(f"User {current_user.id} fetched {len(drafts)} drafts.")
    return drafts or []

@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """ Retrieve a specific article by its ID. """
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    logger.info(f"Article '{article.title}' (ID: {article_id}) retrieved.")
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
def update_existing_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authors to update their own articles, and admins to edit any. """
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Allow update if the user is the author or an admin
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own articles")

    # Only validate fields that were explicitly provided in the request
    if article_data.title is not None and len(article_data.title) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be at least 5 characters long."
        )
    if article_data.content is not None and len(article_data.content) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be at least 10 characters long."
        )

    updated_article = update_article(db, article.id, article_data)
    logger.info(f"User {current_user.id} updated article '{article.title}' (ID: {article_id})")
    return updated_article

@router.delete("/{article_id}")
def delete_existing_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authors to delete their own articles, and admins to remove any. """
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Allow deletion if the user is the author or an admin
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own articles")

    delete_article(db, article_id)
    logger.info(f"User {current_user.id} deleted article '{article.title}' (ID: {article_id})")
    return {"detail": f"Article '{article.title}' deleted successfully"}

# Share
@router.get("/{article_id}/share")
def share_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        logger.warning(f"Article with ID {article_id} not found.")
        raise HTTPException(status_code=404, detail="Article not found")

    share_url = f"{FRONTEND_URL}/posts/{article_id}"
    logger.info(f"Generated share URL for article {article_id}: {share_url}")
    return {"share_url": share_url}

@router.put("/{article_id}/publish")
async def toggle_publish(
    article_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    if article.status == ArticleStatus.PUBLISHED:
        article.status = ArticleStatus.DRAFT
        article.published_date = None
    else:
        article.status = ArticleStatus.PUBLISHED
        article.published_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(article)
    return {"status": article.status, "published_date": article.published_date}
