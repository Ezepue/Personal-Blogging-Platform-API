from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Optional
import logging

from database import get_db
from schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from utils.auth_helpers import get_current_user, get_optional_user, is_admin
from utils.db_helpers import (
    create_new_comment, get_comments_by_article, get_comment_by_id, delete_comment, get_article_by_id
)
from utils.notification_helper import send_notification_to_user
from models.user import UserDB
from models.article import ArticleDB
from models.comment import CommentDB
from models.comment_like import CommentLikeDB

logger = logging.getLogger(__name__)

router = APIRouter()


def _with_like_state(db: Session, comments: List[CommentDB], user: Optional[UserDB]) -> List[CommentResponse]:
    """Attach liked_by_me to serialized comments for the requesting user."""
    liked_ids = set()
    if user is not None and comments:
        ids = [c.id for c in comments]
        liked_ids = {
            row[0]
            for row in db.query(CommentLikeDB.comment_id)
            .filter(CommentLikeDB.user_id == user.id, CommentLikeDB.comment_id.in_(ids))
            .all()
        }
    result = []
    for c in comments:
        item = CommentResponse.model_validate(c)
        item.liked_by_me = c.id in liked_ids
        result.append(item)
    return result


@router.post("/", response_model=CommentResponse)
async def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Comment on an article, or reply to an existing comment via parent_id. """
    article = get_article_by_id(db, comment.article_id)

    parent = None
    if comment.parent_id is not None:
        parent = get_comment_by_id(db, comment.parent_id)
        if parent.article_id != comment.article_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment belongs to a different article",
            )

    new_comment = create_new_comment(db, comment, author_id=current_user.id)
    logger.info(f"User {current_user.id} commented on article '{article.title}' (ID: {comment.article_id})")

    # Notify the article author (new comment) or the parent comment's author (reply).
    try:
        if parent is not None and parent.user_id != current_user.id:
            await send_notification_to_user(
                db=db,
                user_id=parent.user_id,
                message=f"{current_user.username} replied to your comment on \"{article.title}\"",
                notif_type="comment",
                extra_data={"article_id": article.id, "comment_id": new_comment.id},
            )
        elif parent is None and article.author_id != current_user.id:
            await send_notification_to_user(
                db=db,
                user_id=article.author_id,
                message=f"{current_user.username} commented on \"{article.title}\"",
                notif_type="comment",
                extra_data={"article_id": article.id, "comment_id": new_comment.id},
            )
    except Exception:
        pass  # notification failure must not fail the comment operation

    return _with_like_state(db, [new_comment], current_user)[0]


@router.get("/{article_id}", response_model=List[CommentResponse])
def list_comments(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_user),
    skip: int = 0,
    limit: int = 100,
):
    """ Retrieve comments (flat list; replies reference parent_id) for an article. """
    limit = min(200, max(1, limit))
    get_article_by_id(db, article_id)  # 404 if missing
    comments = get_comments_by_article(db, article_id, skip, limit)
    return _with_like_state(db, comments, current_user)


@router.put("/{comment_id}", response_model=CommentResponse)
def edit_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """ Edit a comment. Only the comment's author may edit it. """
    comment = get_comment_by_id(db, comment_id)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")

    comment.content = data.content
    comment.updated_date = func.now()
    db.commit()
    db.refresh(comment)
    return _with_like_state(db, [comment], current_user)[0]


@router.post("/{comment_id}/like", response_model=CommentResponse)
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """ Like a comment (idempotent errors: 400 when already liked). """
    comment = get_comment_by_id(db, comment_id)
    try:
        db.add(CommentLikeDB(user_id=current_user.id, comment_id=comment_id))
        db.flush()
        likes = db.query(func.count(CommentLikeDB.id)).filter(CommentLikeDB.comment_id == comment_id).scalar()
        comment.likes_count = likes
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already liked this comment")
    db.refresh(comment)
    return _with_like_state(db, [comment], current_user)[0]


@router.delete("/{comment_id}/like", response_model=CommentResponse)
def unlike_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """ Remove a like from a comment. """
    comment = get_comment_by_id(db, comment_id)
    like = db.query(CommentLikeDB).filter(
        CommentLikeDB.user_id == current_user.id,
        CommentLikeDB.comment_id == comment_id,
    ).one_or_none()
    if like is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not liked this comment")
    db.delete(like)
    db.flush()
    likes = db.query(func.count(CommentLikeDB.id)).filter(CommentLikeDB.comment_id == comment_id).scalar()
    comment.likes_count = likes
    db.commit()
    db.refresh(comment)
    return _with_like_state(db, [comment], current_user)[0]


@router.delete("/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Allow the comment owner, the article's author, and admins to delete a comment."""
    comment = get_comment_by_id(db, comment_id)

    is_owner = comment.user_id == current_user.id
    article = db.query(ArticleDB).filter(ArticleDB.id == comment.article_id).first()
    is_article_author = article is not None and article.author_id == current_user.id

    if not (is_owner or is_article_author or is_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    delete_comment(db, comment_id)
    logger.info(f"User {current_user.id} deleted comment {comment_id} on article ID {comment.article_id}")
    return {"status": "success", "detail": f"Comment {comment_id} deleted successfully"}
