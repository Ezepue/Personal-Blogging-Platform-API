from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timezone
import logging

from app.db.session import get_db
from app.core.config import FRONTEND_URL
from app.models.article import ArticleDB
from app.models.follow import FollowDB
from app.models.user import UserDB
from app.models.view_history import ViewHistoryDB
from app.models.enums import ArticleStatus
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, TagCount, SearchResults,
)
from app.api.deps import (
    create_preview_token, get_current_user, get_optional_user, is_admin,
    require_admin, verify_preview_token,
)
from app.services import (
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
    response: Response,
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = "latest",
    skip: int = 0,
    limit: int = 10,
):
    """Public feed of PUBLISHED articles.

    Supports search/category/tag filters and latest/trending/top sorting; the
    total matching count is exposed via the X-Total-Count header so clients
    can paginate.
    """
    limit = min(50, max(1, limit))
    if sort not in VALID_SORTS:
        sort = "latest"

    articles, total = get_articles(
        db, search=search, category=category, tag=tag, skip=skip, limit=limit,
        status=ArticleStatus.PUBLISHED, sort=sort, with_total=True,
    )
    response.headers["X-Total-Count"] = str(total)
    return articles or []


@router.get("/featured", response_model=List[ArticleResponse])
def featured_articles(db: Session = Depends(get_db), limit: int = 6):
    """Editors' picks: published stories flagged by admins."""
    limit = min(12, max(1, limit))
    return get_articles(db, status=ArticleStatus.PUBLISHED, featured_only=True, limit=limit)


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
            ArticleDB.is_unlisted == False,
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
        .filter(ArticleDB.status == ArticleStatus.PUBLISHED, ArticleDB.is_unlisted == False)
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
    """Site-wide search across published articles and authors.

    Supports the operators ``author:<username>`` and ``tag:<tag>``; remaining
    words are matched against titles, subtitles, and body text.
    """
    limit = min(50, max(1, limit))
    q = q.strip()
    if not q:
        return {"articles": [], "authors": []}

    author_filter = None
    tag_filter = None
    words = []
    for token in q.split():
        if token.lower().startswith("author:") and len(token) > 7:
            author_filter = token[7:]
        elif token.lower().startswith("tag:") and len(token) > 4:
            tag_filter = token[4:]
        else:
            words.append(token)
    text_query = " ".join(words) or None

    articles = get_articles(
        db, search=text_query, author_username=author_filter, tag=tag_filter,
        status=ArticleStatus.PUBLISHED, limit=limit,
    )
    author_term = author_filter or text_query
    authors = []
    if author_term:
        authors = (
            db.query(UserDB)
            .filter(
                UserDB.is_active == True,
                or_(
                    UserDB.username.icontains(author_term, autoescape=True),
                    UserDB.bio.icontains(author_term, autoescape=True),
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
        if viewer is not None:
            # Upsert the reader's history entry so "recently viewed" stays fresh.
            existing = db.query(ViewHistoryDB).filter(
                ViewHistoryDB.user_id == viewer.id,
                ViewHistoryDB.article_id == article.id,
            ).first()
            if existing:
                existing.viewed_at = datetime.utcnow()
            else:
                db.add(ViewHistoryDB(user_id=viewer.id, article_id=article.id))
        db.commit()
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
        ArticleDB.is_unlisted == False,
        ArticleDB.id != article.id,
    )
    if filters:
        query = query.filter(or_(*filters))
    related = query.order_by(ArticleDB.views_count.desc(), ArticleDB.id.desc()).limit(limit).all()

    if len(related) < limit:
        seen = {a.id for a in related} | {article.id}
        extra = (
            db.query(ArticleDB)
            .filter(
                ArticleDB.status == ArticleStatus.PUBLISHED,
                ArticleDB.is_unlisted == False,
                ArticleDB.id.notin_(seen),
            )
            .order_by(ArticleDB.id.desc())
            .limit(limit - len(related))
            .all()
        )
        related.extend(extra)
    return related


@router.get("/{article_id}/preview-token")
def issue_preview_token(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Issue a shareable secret link token for one of the author's drafts."""
    article = get_article_by_id(db, article_id)
    if article.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only the author can share a draft preview")
    token = create_preview_token(article.id, current_user.id)
    return {"token": token, "url": f"{FRONTEND_URL}/preview/{token}"}


@router.get("/preview/{token}", response_model=ArticleResponse)
def read_draft_preview(token: str, db: Session = Depends(get_db)):
    """Read a draft through a preview token, without authentication."""
    article_id = verify_preview_token(token)
    if article_id is None:
        raise HTTPException(status_code=404, detail="Preview link is invalid or has expired")
    return get_article_by_id(db, article_id)


@router.put("/{article_id}/feature", response_model=ArticleResponse)
def toggle_feature(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """Toggle a story in or out of the editors' picks (admins only)."""
    article = get_article_by_id(db, article_id)
    article.is_featured = not article.is_featured
    db.commit()
    db.refresh(article)
    return article


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
