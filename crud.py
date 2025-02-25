from sqlalchemy.orm import Session
from models import UserDB, ArticleDB
from schemas import UserCreate, ArticleCreate
from auth import hash_password
from fastapi import HTTPException
import json
from datetime import datetime

# ---------------------- USER OPERATIONS ----------------------

def create_user(db: Session, user: UserCreate):
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken!")

    hashed_password = hash_password(user.password)
    db_user = UserDB(username=user.username, hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# ---------------------- ARTICLE OPERATIONS ----------------------

def create_article(db: Session, article_data: ArticleCreate, user_id: int):
    db_article = ArticleDB(
        title=article_data.title,
        content=article_data.content,
        tags=json.dumps(article_data.tags),  # Store tags as a JSON string
        user_id=user_id
    )
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    # Convert tags back to list before returning
    db_article.tags = json.loads(db_article.tags)
    return db_article

def get_articles(db: Session):
    articles = db.query(ArticleDB).all()
    for article in articles:
        article.tags = json.loads(article.tags) if isinstance(article.tags, str) else article.tags
    return articles

def get_article(db: Session, article_id: int):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if article:
        article.tags = json.loads(article.tags) if isinstance(article.tags, str) else article.tags
    return article

def update_article(db: Session, article_id: int, article_data: ArticleCreate, user_id: int):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")

    article.title = article_data.title
    article.content = article_data.content
    article.tags = json.dumps(article_data.tags)  # Ensure tags are stored as JSON
    article.updated_date = datetime.utcnow()

    db.commit()
    db.refresh(article)

    article.tags = json.loads(article.tags)  # Convert back to list before returning
    return article

def delete_article(db: Session, article_id: int, user_id: int):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")

    db.delete(article)
    db.commit()
    return True
