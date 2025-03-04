from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List  # Import List for response model
from schemas import CommentCreate, CommentResponse
from database import get_db
from models import CommentDB, ArticleDB, UserDB
from auth import get_current_user

router = APIRouter()

@router.post("/{article_id}/comments", response_model=CommentResponse)
def add_comment(
    article_id: int, 
    comment: CommentCreate, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)  #Explicit typing
):
    """ Add a comment to an article. """
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    new_comment = CommentDB(
        content=comment.content, 
        user_id=user.id, 
        article_id=article_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.get("/{article_id}/comments", response_model=List[CommentResponse])
def get_comments(article_id: int, db: Session = Depends(get_db)):
    """ Retrieve all comments for a specific article. """
    comments = db.query(CommentDB).filter(CommentDB.article_id == article_id).all()
    return comments

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)  #Explicit typing
):
    """ Delete a comment. Only the comment owner can delete their comment. """
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}
