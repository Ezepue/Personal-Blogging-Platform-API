from sqlalchemy.orm import Session
from models import UserDB, ArticleDB, LikeDB, CommentDB, ArticleStatus
from schemas import UserCreate, ArticleCreate, ArticleUpdate, CommentCreate
from auth import hash_password
from fastapi import HTTPException
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
    published_date = datetime.utcnow() if article_data.status == ArticleStatus.PUBLISHED else None

    db_article = ArticleDB(
        title=article_data.title,
        content=article_data.content,
        tags=article_data.tags,  # JSON already handled by SQLAlchemy
        category=article_data.category,
        status=article_data.status,
        published_date=published_date,
        user_id=user_id
    )

    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    return db_article

def get_articles(db: Session, title: str = None, tag: str = None, category: str = None, user_id: int = None, status: ArticleStatus = None, limit: int = 10, offset: int = 0):
    query = db.query(ArticleDB)

    if title:
        query = query.filter(ArticleDB.title.ilike(f"%{title}%"))
    
    if tag:
        query = query.filter(ArticleDB.tags.contains(tag))
    
    if category:
        query = query.filter(ArticleDB.category == category)
    
    if user_id:
        query = query.filter(ArticleDB.user_id == user_id)
    
    if status:
        query = query.filter(ArticleDB.status == status)

    return query.limit(limit).offset(offset).all()

def get_article(db: Session, article_id: int):
    return db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

def update_article(db: Session, article_id: int, article_data: ArticleUpdate, user_id: int):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")

    if article_data.title is not None:
        article.title = article_data.title
    if article_data.content is not None:
        article.content = article_data.content
    if article_data.tags is not None:
        article.tags = article_data.tags
    if article_data.category is not None:
        article.category = article_data.category
    if article_data.status is not None:
        article.status = article_data.status
        article.published_date = datetime.utcnow() if article_data.status == ArticleStatus.PUBLISHED else None

    article.updated_date = datetime.utcnow()

    db.commit()
    db.refresh(article)

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

# ---------------------- LIKE OPERATIONS ----------------------

def like_article(db: Session, article_id: int, user_id: int):
    existing_like = db.query(LikeDB).filter(LikeDB.article_id == article_id, LikeDB.user_id == user_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked this article")

    like = LikeDB(user_id=user_id, article_id=article_id)
    db.add(like)
    db.commit()
    return {"message": "Article liked"}

def unlike_article(db: Session, article_id: int, user_id: int):
    like = db.query(LikeDB).filter(LikeDB.article_id == article_id, LikeDB.user_id == user_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return {"message": "Like removed"}

def get_article_likes(db: Session, article_id: int):
    return db.query(LikeDB).filter(LikeDB.article_id == article_id).count()
