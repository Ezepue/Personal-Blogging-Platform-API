"""Article domain: creation, querying, visibility, and lifecycle."""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.article import ArticleDB
from app.models.comment import CommentDB
from app.models.enums import ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.utils.sanitize import sanitize_html
from app.utils.text import unique_slug, reading_time_minutes, word_count

logger = logging.getLogger(__name__)

VALID_SORTS = {"latest", "trending", "top"}


def create_new_article(db: Session, article_data: ArticleCreate, author_id: int) -> ArticleDB:
    """Create an article: sanitize content, derive slug/reading-time/word-count."""
    published_date = (
        datetime.now(timezone.utc) if article_data.status == ArticleStatus.PUBLISHED else None
    )
    content = sanitize_html(article_data.content)
    new_article = ArticleDB(
        title=article_data.title,
        subtitle=article_data.subtitle,
        slug=unique_slug(db, article_data.title),
        content=content,
        category=article_data.category,
        cover_image_url=article_data.cover_image_url,
        tags=article_data.tags or [],
        author_id=author_id,
        status=article_data.status,
        is_unlisted=article_data.is_unlisted,
        published_date=published_date,
        reading_time_minutes=reading_time_minutes(content),
        word_count=word_count(content),
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article


def get_articles(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_username: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    status: Optional[ArticleStatus] = ArticleStatus.PUBLISHED,
    sort: str = "latest",
    include_unlisted: bool = False,
    featured_only: bool = False,
    with_total: bool = False,
):
    """Query articles with filtering and sorting.

    Unlisted stories never appear in list contexts unless explicitly included
    (they remain reachable by direct link). Returns a list, or a
    ``(list, total)`` pair when ``with_total`` is set.
    """
    skip = max(0, skip)
    query = db.query(ArticleDB)

    if status is not None:
        query = query.filter(ArticleDB.status == status)
    if not include_unlisted:
        query = query.filter(ArticleDB.is_unlisted == False)
    if featured_only:
        query = query.filter(ArticleDB.is_featured == True)

    if search:
        query = query.filter(or_(
            ArticleDB.title.icontains(search, autoescape=True),
            ArticleDB.subtitle.icontains(search, autoescape=True),
            ArticleDB.content.icontains(search, autoescape=True),
        ))
    if category:
        query = query.filter(func.lower(ArticleDB.category) == func.lower(category))
    if tag:
        query = query.filter(ArticleDB.tags.contains([tag]))
    if author_username:
        from app.models.user import UserDB
        query = query.join(UserDB, UserDB.id == ArticleDB.author_id).filter(
            func.lower(UserDB.username) == author_username.lower()
        )

    total = query.count() if with_total else None

    if sort == "trending":
        order = (ArticleDB.views_count.desc(), ArticleDB.id.desc())
    elif sort == "top":
        order = (ArticleDB.likes_count.desc(), ArticleDB.id.desc())
    else:
        order = (ArticleDB.id.desc(),)

    rows = query.order_by(*order).offset(skip).limit(limit).all()
    return (rows, total) if with_total else rows


def get_user_drafts(db: Session, author_id: int, skip: int = 0, limit: int = 50) -> List[ArticleDB]:
    """The author's own drafts, newest first."""
    return (
        db.query(ArticleDB)
        .filter(ArticleDB.author_id == author_id, ArticleDB.status == ArticleStatus.DRAFT)
        .order_by(ArticleDB.id.desc())
        .offset(max(0, skip))
        .limit(limit)
        .all()
    )


def get_article_by_id(db: Session, article_id: int) -> ArticleDB:
    """Fetch an article by id, raising 404 when absent."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )
    return article


def update_article(db: Session, article_id: int, article_data: ArticleUpdate) -> ArticleDB:
    """Apply a partial update, keeping derived fields and publish state consistent."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).one_or_none()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )

    data = article_data.model_dump(exclude_unset=True)
    if data.get("content") is not None:
        data["content"] = sanitize_html(data["content"])
        article.reading_time_minutes = reading_time_minutes(data["content"])
        article.word_count = word_count(data["content"])

    # Regenerate the slug only when the title actually changes, excluding this
    # article from the uniqueness check so an unchanged title doesn't churn the URL.
    new_title = data.get("title")
    if new_title and new_title != article.title:
        article.slug = unique_slug(db, new_title, exclude_id=article.id)

    for key, value in data.items():
        setattr(article, key, value)

    if "status" in data:
        if data["status"] == ArticleStatus.PUBLISHED and article.published_date is None:
            article.published_date = datetime.now(timezone.utc)
        elif data["status"] == ArticleStatus.DRAFT:
            article.published_date = None

    try:
        db.commit()
        db.refresh(article)
        return article
    except SQLAlchemyError as commit_error:
        db.rollback()
        logger.error(f"DB error updating article {article_id}: {commit_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article",
        )


def delete_article(db: Session, article_id: int) -> None:
    """Hard-delete an article and its comments."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.query(CommentDB).filter(CommentDB.article_id == article_id).delete(synchronize_session=False)
    db.delete(article)
    db.commit()


def get_article_with_likes(db: Session, article_id: int) -> ArticleDB:
    """Fetch an article for like operations, raising 404 when absent."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


def can_view_article(article: ArticleDB, user) -> bool:
    """Published articles are public; drafts/deleted are visible only to the author or an admin."""
    if article.status == ArticleStatus.PUBLISHED:
        return True
    if user is None:
        return False
    from app.models.enums import UserRole
    return article.author_id == user.id or user.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}
