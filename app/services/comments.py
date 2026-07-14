"""Comment domain: threads, editing, and moderation-aware queries."""
import logging
import re
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import CommentDB
from app.models.user import UserDB
from app.schemas.comment import CommentCreate

logger = logging.getLogger(__name__)

MENTION_RE = re.compile(r"@([a-zA-Z0-9_]{3,30})")


def create_new_comment(db: Session, comment_data: CommentCreate, author_id: int) -> CommentDB:
    """Create a comment or threaded reply."""
    new_comment = CommentDB(
        article_id=comment_data.article_id,
        content=comment_data.content,
        user_id=author_id,
        parent_id=comment_data.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def extract_mentions(db: Session, content: str, exclude_user_id: int) -> List[UserDB]:
    """Resolve @username tokens in a comment to real, active users.

    The comment author is excluded so self-mentions never notify.
    """
    usernames = {m.lower() for m in MENTION_RE.findall(content)}
    if not usernames:
        return []
    users = (
        db.query(UserDB)
        .filter(UserDB.username.in_(usernames), UserDB.is_active == True)
        .all()
    )
    return [u for u in users if u.id != exclude_user_id]


def get_comments_by_article(
    db: Session, article_id: int, skip: int = 0, limit: int = 100, sort: str = "new"
) -> List[CommentDB]:
    """Comments for an article, excluding deleted; sort by recency or likes."""
    query = db.query(CommentDB).filter(
        CommentDB.article_id == article_id, CommentDB.is_deleted == False
    )
    if sort == "top":
        query = query.order_by(CommentDB.likes_count.desc(), CommentDB.created_date.desc())
    else:
        query = query.order_by(CommentDB.created_date.desc())
    return query.offset(skip).limit(limit).all()


def get_comment_by_id(db: Session, comment_id: int) -> CommentDB:
    """Fetch a comment by id, raising 404 when absent."""
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found",
        )
    return comment


def delete_comment(db: Session, comment_id: int) -> None:
    """Delete a comment by id. Authorization is the caller's responsibility."""
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()


def get_all_comments(db: Session) -> List[CommentDB]:
    """All comments, newest first (admin listing)."""
    return db.query(CommentDB).order_by(CommentDB.id.desc()).all()
