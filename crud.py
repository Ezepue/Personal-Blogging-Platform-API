from sqlalchemy.orm import Session
from models import UserDB, ArticleDB
from schemas import UserCreate, ArticleCreate
from auth import hash_password
from fastapi import HTTPException

# ---------------------- USER OPERATIONS ----------------------

def create_user(db: Session, user: UserCreate):
    """
    Create a new user in the database after checking for duplicates and hashing the password.
    """
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

def create_article(db: Session, article_data: ArticleCreate):
    """
    Create a new article in the database.
    """
    db_article = ArticleDB(
        title=article_data.title,
        content=article_data.content,
        tags=",".join(article_data.tags) if article_data.tags else None,
        published_date=article_data.published_date,
        updated_date=article_data.updated_date
    )

    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    return db_article

def get_articles(db: Session):
    """
    Retrieve all articles from the database.
    """
    return db.query(ArticleDB).all()

def get_article(db: Session, article_id: int):
    """
    Retrieve a single article by its ID.
    """
    return db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

def delete_article(db: Session, article_id: int):
    """
    Delete an article by its ID, if it exists.
    """
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        return True
    return False  # Return False if article was not found
