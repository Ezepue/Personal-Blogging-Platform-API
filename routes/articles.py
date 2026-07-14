from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timezone
import logging

from database import get_db
from config import FRONTEND_URL
from models.article import ArticleDB
from models.follow import FollowDB
from models.user import UserDB
from models.enums import ArticleStatus
from schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, TagCount, SearchResults, SearchAuthor,
)
from utils.auth_helpers import get_current_user, get_optional_user, is_admin
from utils.db_helpers import (
    create_new_article, get_article_by_id,
    update_article, delete_article, get_articles, get_user_drafts
)

logger = logging.getLogger(__name__)

router = APIRouter()

VALID_SORTS = {"latest", "trending", "top"}


def _can_view_article(article: ArticleDB, user: Optional[UserDB]) -> bool:
    """Published articles are public; drafts/deleted are visible only to the author or an admin."""
    if article.status == ArticleStatus.PUBLISHED:
        return True
    if user is None:
        return False
    return article.author_id == user.id or is_admin(user)


@router.post("", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Create a new article. Only authenticated users can post. """
    new_article = create_new_article(db, article, author_id=current_user.id)
    logger.info(f"User {current_user.id} created article '{new_article.title}' (ID: {new_article.id})")
    return new_article


@router.get("", response_model=List[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = "latest",
    skip: int = 0,
    limit: int = 10,
):
    """ Public feed of PUBLISHED articles with search/category/tag filters and sorting. """
    limit = min(50, max(1, limit))
    if sort not in VALID_SORTS:
        sort = "latest"

    articles = get_articles(
        db, search=search, category=category, tag=tag, skip=skip, limit=limit,
        status=ArticleStatus.PUBLISHED, sort=sort,
    )
    return articles or []


@router.get("/feed", response_model=List[ArticleResponse])
def following_feed(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    """ Personalized feed: published articles from authors the user follows. """
    limit = min(50, max(1, limit))
    followed_ids = db.query(FollowDB.followed_id).filter(FollowDB.follower_id == current_user.id)
    articles = (
        db.query(ArticleDB)
        .filter(
            ArticleDB.author_id.in_(followed_ids.subquery()),
            ArticleDB.status == ArticleStatus.PUBLISHED,
        )
        .order_by(ArticleDB.published_date.desc().nulls_last(), ArticleDB.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return articles


@router.get("/my-drafts", response_model=List[ArticleResponse])
def list_my_drafts(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    """ Return all DRAFT articles belonging to the authenticated user. """
    limit = min(100, max(1, limit))
    drafts = get_user_drafts(db, author_id=current_user.id, skip=skip, limit=limit)
    return drafts or []


@router.get("/tags", response_model=List[TagCount])
def list_tags(db: Session = Depends(get_db), limit: int = 30):
    """ All tags used across published articles, with usage counts (most used first). """
    limit = min(100, max(1, limit))
    tag_expr = func.jsonb_array_elements_text(ArticleDB.tags).label("tag")
    rows = (
        db.query(tag_expr, func.count().label("count"))
        .filter(ArticleDB.status == ArticleStatus.PUBLISHED)
        .group_by("tag")
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )
    return [{"tag": r.tag, "count": r.count} for r in rows]


@router.get("/search", response_model=SearchResults)
def search_everything(
    q: str,
    db: Session = Depends(get_db),
    limit: int = 20,
):
    """ Site-wide search across published articles and authors. """
    limit = min(50, max(1, limit))
    q = q.strip()
    if not q:
        return {"articles": [], "authors": []}

    articles = get_articles(db, search=q, status=ArticleStatus.PUBLISHED, limit=limit)
    authors = (
        db.query(UserDB)
        .filter(
            UserDB.is_active == True,
            or_(
                UserDB.username.icontains(q, autoescape=True),
                UserDB.bio.icontains(q, autoescape=True),
            ),
        )
        .limit(10)
        .all()
    )
    return {"articles": articles, "authors": authors}


@router.get("/slug/{slug}", response_model=ArticleResponse)
def read_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_user),
):
    """ Retrieve an article by its slug. Drafts/deleted are private. """
    article = db.query(ArticleDB).filter(ArticleDB.slug == slug).first()
    if not article or not _can_view_article(article, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    _count_view(db, article, current_user)
    return article


@router.get("/{article_id}", response_model=ArticleResponse)
def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_user),
):
    """ Retrieve a specific article by its ID. Drafts/deleted are private. """
    article = get_article_by_id(db, article_id)
    if not _can_view_article(article, current_user):
        # 404 rather than 403 so we don't reveal that a draft/deleted article exists.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    _count_view(db, article, current_user)
    return article


def _count_view(db: Session, article: ArticleDB, viewer: Optional[UserDB]) -> None:
    """Increment the view counter for published articles (not for the author's own views)."""
    if article.status != ArticleStatus.PUBLISHED:
        return
    if viewer is not None and viewer.id == article.author_id:
        return
    try:
        db.query(ArticleDB).filter(ArticleDB.id == article.id).update(
            {ArticleDB.views_count: ArticleDB.views_count + 1}, synchronize_session=False
        )
        db.commit()
        # keep the in-memory object consistent with what we just wrote
        article.views_count = (article.views_count or 0) + 1
    except Exception:
        db.rollback()  # view counting must never break reads


@router.get("/{article_id}/related", response_model=List[ArticleResponse])
def related_articles(
    article_id: int,
    db: Session = Depends(get_db),
    limit: int = 4,
):
    """ Published articles related by shared tags or category (excluding the article itself). """
    limit = min(10, max(1, limit))
    article = get_article_by_id(db, article_id)

    filters = []
    if article.tags:
        filters.extend(ArticleDB.tags.contains([t]) for t in article.tags[:5])
    if article.category:
        filters.append(func.lower(ArticleDB.category) == func.lower(article.category))

    query = db.query(ArticleDB).filter(
        ArticleDB.status == ArticleStatus.PUBLISHED,
        ArticleDB.id != article.id,
    )
    if filters:
        query = query.filter(or_(*filters))
    related = query.order_by(ArticleDB.views_count.desc(), ArticleDB.id.desc()).limit(limit).all()

    # Backfill with recent posts when there aren't enough related matches.
    if len(related) < limit:
        seen = {a.id for a in related} | {article.id}
        extra = (
            db.query(ArticleDB)
            .filter(ArticleDB.status == ArticleStatus.PUBLISHED, ArticleDB.id.notin_(seen))
            .order_by(ArticleDB.id.desc())
            .limit(limit - len(related))
            .all()
        )
        related.extend(extra)
    return related


@router.put("/{article_id}", response_model=ArticleResponse)
def update_existing_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authors to update their own articles, and admins to edit any. """
    article = get_article_by_id(db, article_id)
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own articles")

    updated_article = update_article(db, article.id, article_data)
    logger.info(f"User {current_user.id} updated article '{article.title}' (ID: {article_id})")
    return updated_article


@router.delete("/{article_id}")
def delete_existing_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authors to delete their own articles, and admins to remove any. """
    article = get_article_by_id(db, article_id)
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own articles")

    delete_article(db, article_id)
    logger.info(f"User {current_user.id} deleted article '{article.title}' (ID: {article_id})")
    return {"detail": f"Article '{article.title}' deleted successfully"}


@router.get("/{article_id}/share")
def share_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_user),
):
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article or not _can_view_article(article, current_user):
        raise HTTPException(status_code=404, detail="Article not found")

    share_url = f"{FRONTEND_URL}/posts/{article_id}"
    return {"share_url": share_url}


@router.put("/{article_id}/publish")
async def toggle_publish(
    article_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = get_article_by_id(db, article_id)
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    if article.status == ArticleStatus.PUBLISHED:
        article.status = ArticleStatus.DRAFT
        article.published_date = None
    else:
        article.status = ArticleStatus.PUBLISHED
        article.published_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(article)
    return {"status": article.status, "published_date": article.published_date}
