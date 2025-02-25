from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ArticleCreate, ArticleResponse
from database import get_db
from crud import create_article, get_articles, get_article
from auth import get_current_user


router = APIRouter()

@router.post("/", response_model=ArticleResponse)
def create_new_article(article: ArticleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Ensure tags is always a list
    tags = article.tags if isinstance(article.tags, list) else []
    
    # Create article with the corrected tags field
    return create_article(db, ArticleCreate(title=article.title, content=article.content, tags=tags), user.id)

@router.get("/", response_model=list[ArticleResponse])
def read_articles(db: Session = Depends(get_db)):
    return get_articles(db)

@router.get("/{id}", response_model=ArticleResponse)
def read_article(id: int, db: Session = Depends(get_db)):
    article = get_article(db, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
