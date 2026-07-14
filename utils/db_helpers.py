import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from models.user import UserDB
from models.article import ArticleDB
from models.comment import CommentDB
from models.refresh_token import RefreshTokenDB
from models.enums import UserRole, ArticleStatus
from schemas.user import UserCreate
from schemas.article import ArticleCreate, ArticleUpdate
from schemas.comment import CommentCreate
from typing import List, Optional
from utils.auth_helpers import hash_password
from utils.sanitize import sanitize_html

# Logger Setup (Fixed Order)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# User operations

def get_user_by_id(db: Session, user_id: int):
    """Retrieve user by ID with error handling."""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_new_user(db: Session, user_data: UserCreate, role: UserRole = UserRole.READER):
    existing_user = db.query(UserDB).filter(
        or_(
            func.lower(UserDB.username) == user_data.username.lower(),
            func.lower(UserDB.email) == user_data.email.lower()
        )
    ).first()
    if existing_user:
        logger.warning(f"User creation failed: Username ({user_data.username}) or Email ({user_data.email}) already taken.")
        raise HTTPException(status_code=400, detail="Username or Email already taken")

    new_user = UserDB(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=hash_password(user_data.password),
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User created: {new_user.username} (ID: {new_user.id}, Role: {new_user.role})")
    return new_user

def update_user_role(db: Session, current_user: UserDB, user_id: int, new_role: str):
    """Update the role of an existing user."""
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change your own role")

    user = get_user_by_id(db, user_id)

    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Super Admins cannot be downgraded")

    if user.role == UserRole[new_role]:  # Convert string to Enum
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this role")

    user.role = UserRole[new_role]
    db.commit()
    db.refresh(user)

    logger.info(f"User {user.username} role updated to {new_role}")
    return user

def promote_user(db: Session, user_id: int, new_role: UserRole):
    """Promote a user to a given role. ``new_role`` is a ``UserRole`` enum member."""
    if not isinstance(new_role, UserRole):
        logger.warning(f"Invalid role assignment attempted: {new_role!r}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = new_role
    db.commit()
    db.refresh(user)

    logger.info(f"User {user.username} (ID: {user.id}) promoted to {new_role.name}")
    return user


def delete_user_from_db(db: Session, user_id: int):
    """Soft delete a user and their articles/comments instead of hard deleting."""
    user = get_user_by_id(db, user_id)

    user.is_active = False

    db.query(ArticleDB).filter(ArticleDB.author_id == user_id).update(
        {ArticleDB.status: ArticleStatus.DELETED}, synchronize_session=False
    )
    db.query(CommentDB).filter(CommentDB.user_id == user_id).update(
        {CommentDB.is_deleted: True}, synchronize_session=False
    )
    # Kill any active sessions so a deactivated account cannot refresh back in.
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == user_id).update(
        {RefreshTokenDB.is_active: False, RefreshTokenDB.revoked: True},
        synchronize_session=False,
    )

    db.commit()
    logger.info(f"User {user.username} and associated content soft deleted.")


def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def update_user_profile(db: Session, user: UserDB, data: dict) -> UserDB:
    ALLOWED_FIELDS = {"username", "email", "bio"}
    for key, value in data.items():
        if key in ALLOWED_FIELDS and value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session) -> List[UserDB]:
    """Fetch all users from the database (empty list when there are none)."""
    users = db.query(UserDB).order_by(UserDB.id).all()
    logger.info(f"Retrieved {len(users)} users from the database")
    return users




# Article operations

def create_new_article(db: Session, article_data: ArticleCreate, author_id: int):
    """Create a new article for the given author."""
    published_date = (
        datetime.now(timezone.utc)
        if article_data.status == ArticleStatus.PUBLISHED
        else None
    )
    new_article = ArticleDB(
        title=article_data.title,
        content=sanitize_html(article_data.content),
        category=article_data.category,
        tags=article_data.tags or [],
        author_id=author_id,
        status=article_data.status,
        published_date=published_date,
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    logger.info(f"Article '{new_article.title}' created by user {author_id}.")
    return new_article

def get_articles(
    db: Session,
    search: str = None,
    category: str = None,
    skip: int = 0,
    limit: int = 10,
    status: ArticleStatus = ArticleStatus.PUBLISHED,
):
    """Fetch articles based on search, category, and status filters."""
    query = db.query(ArticleDB)

    # Filter by status (defaults to PUBLISHED for public feeds)
    if status is not None:
        query = query.filter(ArticleDB.status == status)

    # Case-insensitive search filter. autoescape=True escapes LIKE wildcards
    # (% and _) in the user-supplied term so they are matched literally.
    if search:
        query = query.filter(or_(
            ArticleDB.title.icontains(search, autoescape=True),
            ArticleDB.content.icontains(search, autoescape=True),
        ))

    # Case-insensitive category filter (avoiding NULL issues)
    if category:
        query = query.filter(func.lower(ArticleDB.category) == func.lower(category))

    return query.order_by(ArticleDB.id.desc()).offset(skip).limit(limit).all()


def get_user_drafts(db: Session, author_id: int, skip: int = 0, limit: int = 50):
    """Fetch DRAFT articles belonging to a specific author."""
    return (
        db.query(ArticleDB)
        .filter(ArticleDB.author_id == author_id, ArticleDB.status == ArticleStatus.DRAFT)
        .order_by(ArticleDB.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_article_by_id(db: Session, article_id: int) -> ArticleDB:
    """Fetch an article by ID, raising 404 when it does not exist."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        logger.warning(f"Article with ID {article_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )
    return article

def update_article(db: Session, article_id: int, article_data: ArticleUpdate) -> ArticleDB:
    """Update an article by ID."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).one_or_none()
    if not article:
        logger.warning(f"Article with ID {article_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )

    data = article_data.model_dump(exclude_unset=True)
    if "content" in data and data["content"] is not None:
        data["content"] = sanitize_html(data["content"])

    for key, value in data.items():
        setattr(article, key, value)

    # Keep published_date consistent with any status change.
    if "status" in data:
        if data["status"] == ArticleStatus.PUBLISHED and article.published_date is None:
            article.published_date = datetime.now(timezone.utc)
        elif data["status"] == ArticleStatus.DRAFT:
            article.published_date = None

    try:
        db.commit()
        db.refresh(article)
        logger.info(f"Article with ID {article_id} updated successfully")
        return article
    except SQLAlchemyError as commit_error:
        db.rollback()
        logger.error(f"DB error while updating article {article_id}: {type(commit_error).__name__}: {commit_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article",
        )


def delete_article(db: Session, article_id: int):
    """Delete an article and its associated comments."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.query(CommentDB).filter(CommentDB.article_id == article_id).delete(synchronize_session=False)
    db.delete(article)
    db.commit()
    logger.info(f"Article '{article.title}' deleted.")

def get_article_with_likes(db: Session, article_id: int):
    """Fetch article and ensure it exists."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article

# Comment operations

def create_new_comment(db: Session, comment_data: CommentCreate, author_id: int):
    """Create a new comment for an article."""
    new_comment = CommentDB(
        article_id=comment_data.article_id,
        content=comment_data.content,
        user_id=author_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    logger.info(f"Comment created by user {author_id} on article {comment_data.article_id}.")
    return new_comment

def get_comments_by_article(db: Session, article_id: int, skip: int = 0, limit: int = 10) -> List[CommentDB]:
    """Retrieve comments for a given article (newest first), excluding deleted ones."""
    comments = (
        db.query(CommentDB)
        .filter(CommentDB.article_id == article_id, CommentDB.is_deleted == False)
        .order_by(CommentDB.created_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info(f"Retrieved {len(comments)} comments for article ID {article_id}")
    return comments

def get_comment_by_id(db: Session, comment_id: int) -> CommentDB:
    """Fetch a single comment by its ID, raising 404 when it does not exist."""
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        logger.warning(f"Comment with ID {comment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found",
        )
    return comment


def delete_comment(db: Session, comment_id: int):
    """Delete a comment by ID. Authorization is enforced by the caller (route)."""
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    logger.info(f"Comment {comment_id} deleted.")
    return {"message": "Comment deleted successfully"}

def get_all_comments(db: Session):
    """Retrieve all comments from the database (empty list when there are none)."""
    comments = db.query(CommentDB).order_by(CommentDB.id.desc()).all()
    logger.info(f"Retrieved {len(comments)} comments from the database.")
    return comments