from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from database import get_db
from models.article import ArticleDB
from models.comment import CommentDB
from models.follow import FollowDB
from models.user import UserDB
from models.enums import ArticleStatus
from schemas.dashboard import DashboardStats, ArticleStats
from utils.auth_helpers import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Author analytics: per-article stats plus aggregate totals."""
    comment_counts = dict(
        db.query(CommentDB.article_id, func.count(CommentDB.id))
        .join(ArticleDB, ArticleDB.id == CommentDB.article_id)
        .filter(ArticleDB.author_id == current_user.id, CommentDB.is_deleted == False)
        .group_by(CommentDB.article_id)
        .all()
    )

    articles = (
        db.query(ArticleDB)
        .filter(ArticleDB.author_id == current_user.id, ArticleDB.status != ArticleStatus.DELETED)
        .order_by(ArticleDB.views_count.desc(), ArticleDB.id.desc())
        .all()
    )

    rows = [
        ArticleStats(
            id=a.id,
            title=a.title,
            slug=a.slug,
            status=a.status.value,
            published_date=a.published_date,
            views_count=a.views_count or 0,
            likes_count=a.likes_count or 0,
            comments_count=comment_counts.get(a.id, 0),
        )
        for a in articles
    ]

    return DashboardStats(
        total_articles=len(rows),
        total_published=sum(1 for r in rows if r.status == "published"),
        total_drafts=sum(1 for r in rows if r.status == "draft"),
        total_views=sum(r.views_count for r in rows),
        total_likes=sum(r.likes_count for r in rows),
        total_comments=sum(r.comments_count for r in rows),
        followers_count=db.query(FollowDB).filter(FollowDB.followed_id == current_user.id).count(),
        following_count=db.query(FollowDB).filter(FollowDB.follower_id == current_user.id).count(),
        articles=rows,
    )
