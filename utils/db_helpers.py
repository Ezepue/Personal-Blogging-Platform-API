from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException

from models.user import UserDB
from models.article import ArticleDB
from models.comment import CommentDB
from models.enums import UserRole
from schemas.user import UserCreate
from schemas.article import ArticleCreate, ArticleUpdate
from schemas.comment import CommentCreate
from utils.auth_helpers import hash_password

def get_user_by_id(db: Session, user_id: int):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_new_user(db: Session, user_data: UserCreate, role: str = "reader"):
    existing_user = db.query(UserDB).filter(
        or_(
            func.lower(UserDB.username) == user_data.username.lower(),
            func.lower(UserDB.email) == user_data.email.lower()
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already taken")

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

def update_user_role(db: Session, current_user: UserDB, user_id: int, new_role: UserRole):
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="You cannot change your own role")
    
    user = get_user_by_id(db, user_id)
    if user.role == UserRole.super_admin:
        raise HTTPException(status_code=400, detail="Super Admins cannot be downgraded")
    if user.role == new_role:
        raise HTTPException(status_code=400, detail="User already has this role")
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

def delete_user_from_db(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    user.is_active = False  # Soft delete

    # Soft delete user’s articles and comments
    db.query(ArticleDB).filter(ArticleDB.author_id == user_id).update({"status": "deleted"}, synchronize_session=False)
    db.query(CommentDB).filter(CommentDB.user_id == user_id).delete(synchronize_session=False)
    
    db.commit()

def create_new_article(db: Session, article_data: ArticleCreate, author_id: int):
    existing_article = db.query(ArticleDB).filter(
        func.lower(ArticleDB.title) == article_data.title.lower()
    ).first()
    if existing_article:
        raise HTTPException(status_code=400, detail="Article title already exists")

    new_article = ArticleDB(
        title=article_data.title,
        content=article_data.content,
        category=article_data.category,
        author_id=author_id,
        status=article_data.status
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

def get_articles(db: Session, search: str = None, category: str = None, skip: int = 0, limit: int = 10):
    query = db.query(ArticleDB)
    if search:
        query = query.filter(or_(
            func.lower(ArticleDB.title).contains(search.lower()),
            func.lower(ArticleDB.content).contains(search.lower())
        ))
    if category:
        query = query.filter(ArticleDB.category == category)
    return query.offset(skip).limit(limit).all()

def delete_article(db: Session, article_id: int):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Delete comments related to the article
    db.query(CommentDB).filter(CommentDB.article_id == article_id).delete(synchronize_session=False)
    db.delete(article)
    db.commit()

def create_new_comment(db: Session, comment_data: CommentCreate, author_id: int):
    new_comment = CommentDB(
        article_id=comment_data.article_id,
        content=comment_data.content,
        user_id=author_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def delete_comment(db: Session, comment_id: int, user: UserDB, allow_admin: bool):
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check if user has permission to delete
    if comment.user_id == user.id or (allow_admin and user.role in {UserRole.admin, UserRole.super_admin}):
        db.delete(comment)
        db.commit()
        return {"message": "Comment deleted successfully"}
    
    raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
