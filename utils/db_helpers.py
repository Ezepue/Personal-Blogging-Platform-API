import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from models.user import UserDB
from models.article import ArticleDB
from models.comment import CommentDB
from models.enums import UserRole
from schemas.user import UserCreate
from schemas.article import ArticleCreate, ArticleUpdate
from schemas.comment import CommentCreate
from typing import List
from utils.auth_helpers import hash_password

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

def promote_user(db: Session, user_id: int, new_role: str):
    """Promote a user to a higher role (e.g., admin, super_admin)."""
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()

        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if new_role not in UserRole.__members__:  # Ensure role is valid
            logger.warning(f"Invalid role assignment attempted: {new_role}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

        user.role = UserRole[new_role]
        db.commit()
        db.refresh(user)

        logger.info(f"User {user.username} (ID: {user.id}) promoted to {new_role}")
        return user
    except Exception as e:
        logger.error(f"Error promoting user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

from models.enums import ArticleStatus

def delete_user_from_db(db: Session, user_id: int):
    """Soft delete user and their articles/comments instead of hard deleting."""
    user = get_user_by_id(db, user_id)
    if not user:
        return

    user.is_active = False
    db.query(ArticleDB).filter(ArticleDB.author_id == user_id).update(
        {ArticleDB.status: ArticleStatus.DELETED}, synchronize_session=False
    )

    db.query(CommentDB).filter(CommentDB.user_id == user_id).update(
        {CommentDB.is_deleted: True }, synchronize_session=False
        )

    db.commit()
    logger.info(f"User {user.username} and associated content soft deleted.")


def get_all_users(db: Session) -> List[UserDB]:
    """Fetch all users from the database."""
    try:
        users = db.query(UserDB).all()

        if not users:
            logger.warning("No users found in the database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )

        logger.info(f"Retrieved {len(users)} users from the database")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )




# Article operations

def create_new_article(db: Session, article_data: ArticleCreate, author_id: int):
    """Create a new article, ensuring the title doesn't already exist."""
    existing_article = db.query(ArticleDB).filter(
        func.lower(ArticleDB.title) == article_data.title.lower()
    ).first()
    if existing_article:
        logger.warning(f"Attempt to create article with existing title: {article_data.title}")
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
    logger.info(f"Article '{new_article.title}' created by user {author_id}.")
    return new_article

def get_articles(db: Session, search: str = None, category: str = None, skip: int = 0, limit: int = 10):
    """Fetch articles based on search and category filters."""
    query = db.query(ArticleDB)

    # Case-insensitive search filter
    if search:
        query = query.filter(or_(
            func.lower(ArticleDB.title).contains(func.lower(search)),
            func.lower(ArticleDB.content).contains(func.lower(search))
        ))

    # Case-insensitive category filter (avoiding NULL issues)
    if category:
        query = query.filter(func.lower(ArticleDB.category) == func.lower(category))

    return query.offset(skip).limit(limit).all()

def get_article_by_id(db: Session, article_id: int) -> ArticleDB:
    """Fetch an article by ID, with logging and error handling."""
    try:
        article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
        if not article:
            logger.warning(f"Article with ID {article_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found"
            )
        logger.info(f"Article with ID {article_id} retrieved successfully")
        return article
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def update_article(db: Session, article_id: int, article_data: ArticleUpdate) -> ArticleDB:
    """Update an article by ID."""
    try:
        article = db.query(ArticleDB).filter(ArticleDB.id == article_id).one_or_none()

        if not article:
            logger.warning(f"Article with ID {article_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found"
            )

        for key, value in article_data.dict(exclude_unset=True).items():
            setattr(article, key, value)

        try:
            db.commit()
            db.refresh(article)
            logger.info(f"Article with ID {article_id} updated successfully")
            return article
        except Exception as commit_error:
            db.rollback()
            logger.error(f"Database commit error while updating article {article_id}: {type(commit_error).__name__}: {commit_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update article"
            )
    except Exception as e:
        logger.error(f"Unexpected error updating article {article_id}: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
    """Retrieve all comments for a given article."""
    try:
        comments = db.query(CommentDB).filter(CommentDB.article_id == article_id).all()

        if not comments:
            logger.warning(f"No comments found for article ID {article_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No comments found for article ID {article_id}"
            )

        logger.info(f"Retrieved {len(comments)} comments for article ID {article_id}")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving comments for article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def get_comment_by_id(db: Session, comment_id: int) -> CommentDB:
    """Fetch a single comment by its ID."""
    try:
        comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()

        if not comment:
            logger.warning(f"Comment with ID {comment_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found"
            )

        logger.info(f"Retrieved comment ID {comment_id}")
        return comment
    except Exception as e:
        logger.error(f"Error retrieving comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def delete_comment(db: Session, comment_id: int, user: UserDB, allow_admin: bool = False):
    """Delete a comment by the user who made it, or by an admin."""
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check if user has permission to delete
    if comment.user_id == user.id or (allow_admin and user.role in {UserRole.admin, UserRole.super_admin}):
        db.delete(comment)
        db.commit()
        logger.info(f"Comment {comment_id} deleted by user {user.id}.")
        return {"message": "Comment deleted successfully"}

    raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

def get_all_comments(db: Session):
    """Retrieve all comments from the database."""
    try:
        comments = db.query(CommentDB).all()

        if not comments:
            logger.info("No comments found in the database.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No comments found"
            )

        logger.info(f"Retrieved {len(comments)} comments from the database.")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )