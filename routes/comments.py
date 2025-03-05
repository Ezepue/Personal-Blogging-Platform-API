from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.comment import CommentCreate, CommentResponse
from utils.auth_helpers import get_current_user, is_admin
from utils.db_helpers import (
    create_new_comment, get_comments_by_article, get_comment_by_id, delete_comment
)
from models.user import UserDB

router = APIRouter()

@router.post("/", response_model=CommentResponse)
def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authenticated users to comment on articles. """
    return create_new_comment(db, comment, author_id=current_user.id)

@router.get("/{article_id}", response_model=List[CommentResponse])
def list_comments(
    article_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """ Retrieve comments for a specific article with pagination. """
    return get_comments_by_article(db, article_id, skip, limit)

@router.delete("/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """ Allow authors and admins to delete comments. """
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.author_id != current_user.id and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )

    delete_comment(db, comment_id)
    return {"detail": "Comment deleted successfully"}
