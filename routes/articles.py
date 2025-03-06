from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from utils.auth_helpers import get_current_user, is_admin
from utils.db_helpers import (
    create_new_article, get_article_by_id, 
    update_article, delete_article, get_articles
)
from models.user import UserDB

router = APIRouter()

@router.post("/", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Create a new article. Only authenticated users can post. """
    return create_new_article(db, article, author_id=current_user.id)

@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db), 
    search: Optional[str] = None, 
    category: Optional[str] = None,
    skip: int = 0, 
    limit: int = 10
):
    """ Fetch all articles with optional search and category filters. """
    return get_articles(db, search, category, skip, limit)

@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """ Retrieve a specific article by its ID. """
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
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

    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own articles")

    return update_article(db, article, article_data)

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

    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own articles")

    delete_article(db, article_id)
    return {"detail": "Article deleted successfully"}
