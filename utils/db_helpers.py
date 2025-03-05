from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from models.user import UserDB
from models.article import ArticleDB
from models.comment import CommentDB
from models.enums import UserRole
from schemas.user import UserCreate
from schemas.article import ArticleCreate, ArticleUpdate
from schemas.comment import CommentCreate
from utils.auth_helpers import hash_password  # Fixed missing import

def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by ID."""
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def create_new_user(db: Session, user_data: UserCreate, role: str = "reader"):
    """Create a new user with a default or specified role."""
    new_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user_role(db: Session, user_id: int, new_role: UserRole):
    """Update a user's role."""
    db_user = get_user_by_id(db, user_id)
    db_user.role = new_role
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_from_db(db: Session, user_id: int):
    """Delete a user from the database."""
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()

def create_new_article(db: Session, article_data: ArticleCreate, author_id: int):
    """Create and store a new article in the database."""
    new_article = ArticleDB(
        title=article_data.title,
        content=article_data.content,
        category=article_data.category,
        user_id=author_id,  # Fixed author_id reference
        status=article_data.status
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

def get_articles(db: Session, search: str = None, category: str = None, skip: int = 0, limit: int = 10):
    """Retrieve articles with optional search and category filters."""
    query = db.query(ArticleDB)
    
    if search:
        query = query.filter(or_(ArticleDB.title.contains(search), ArticleDB.content.contains(search)))
    
    if category:
        query = query.filter(ArticleDB.category == category)
    
    return query.offset(skip).limit(limit).all()

def get_article_by_id(db: Session, article_id: int):
    """Retrieve an article by its ID."""
    return db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    """Retrieve all articles with pagination."""
    return db.query(ArticleDB).offset(skip).limit(limit).all()


def update_article(db: Session, article: ArticleDB, article_data: ArticleUpdate):
    """Update an article's fields."""
    for key, value in article_data.dict(exclude_unset=True).items():
        setattr(article, key, value)
    
    db.commit()
    db.refresh(article)
    return article

def delete_article(db: Session, article: ArticleDB):
    """Delete an article from the database."""
    db.delete(article)
    db.commit()

def create_new_comment(db: Session, comment_data: CommentCreate, author_id: int):
    """Create a new comment in the database."""
    new_comment = CommentDB(
        article_id=comment_data.article_id,
        content=comment_data.content,
        user_id=author_id  # Fixed incorrect field name
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def get_comments_by_article(db: Session, article_id: int, skip: int = 0, limit: int = 10):
    """Retrieve comments for a given article with pagination."""
    return db.query(CommentDB).filter(CommentDB.article_id == article_id).offset(skip).limit(limit).all()

def get_comment_by_id(db: Session, comment_id: int):
    """Retrieve a comment by its ID."""
    return db.query(CommentDB).filter(CommentDB.id == comment_id).first()

def delete_comment(db: Session, comment: CommentDB):
    """Delete a comment from the database."""
    db.delete(comment)
    db.commit()

def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    """Retrieve all users with pagination."""
    return db.query(UserDB).offset(skip).limit(limit).all()

def promote_user(db: Session, user_id: int, new_role: UserRole):
    """Promote a user to a higher role (Admin or Super Admin)."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.super_admin:
        raise HTTPException(status_code=400, detail="User is already a Super Admin")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

def get_all_comments(db: Session, skip: int = 0, limit: int = 10):
    """Retrieve all comments with pagination."""
    return db.query(CommentDB).offset(skip).limit(limit).all()
