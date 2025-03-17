from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db
from models.article import ArticleDB
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from utils.auth_helpers import get_current_user, is_admin
from utils.db_helpers import (
    create_new_article, get_article_by_id,
    update_article, delete_article, get_articles
)
from models.user import UserDB

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ArticleResponse)
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

@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """ Fetch all articles with optional search and category filters. """

    # Restrict pagination limits
    limit = min(50, max(1, limit))

    # Modify the database query to handle search and category filters
    articles = get_articles(db, search=search, category=category, skip=skip, limit=limit)

    logger.info(f"Fetched {len(articles)} articles (Search: '{search}', Category: '{category}').")

    return articles or []

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

    # Ensure title and content are valid (Add custom validations if needed)
    if not article_data.title or len(article_data.title) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be at least 5 characters long."
        )
    if not article_data.content or len(article_data.content) < 10:
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
@router.get("/articles/{id}/share")
def share_article(id: int, db: Session = Depends(get_db)):
    article = db.query(ArticleDB).filter(ArticleDB.id == id).first()
    if not article:
        logger.warning(f"Article with ID {id} not found.")
        raise HTTPException(status_code=404, detail="Article not found")

    share_url = f"http://127.0.0.1:8000/articles/{id}"
    logger.info(f"Generated share URL for article {id}: {share_url}")
    return {"share_url": share_url}
