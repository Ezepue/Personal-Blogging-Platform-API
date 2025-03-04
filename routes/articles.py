from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from schemas import ArticleCreate, ArticleUpdate, ArticleResponse
from database import get_db
from crud import (
    create_article, get_articles, get_article, 
    update_article, delete_article, like_article, 
    unlike_article, get_article_likes
)
from auth import get_current_user
from models import UserRole, UserDB, ArticleStatus

router = APIRouter()

# Create an article (Admin, Author only)
@router.post("/", response_model=ArticleResponse)
def create_new_article(
    article: ArticleCreate, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Create a new article. Only authors & admins are allowed. """
    if user.role not in [UserRole.author, UserRole.admin]:  
        raise HTTPException(status_code=403, detail="Only authors and admins can create articles")

    tags = article.tags if isinstance(article.tags, list) else []  # Ensure tags is a list
    
    return create_article(
        db,
        ArticleCreate(
            title=article.title,
            content=article.content,
            tags=tags,
            category=article.category,
            status=article.status
        ),
        user.id
    )

# Get all articles 
@router.get("/", response_model=list[ArticleResponse])
def read_articles(
    db: Session = Depends(get_db),
    user: UserDB = Depends(get_current_user),  
    title: str = Query(None, description="Search by article title"),
    tag: str = Query(None, description="Filter by tag"),
    category: str = Query(None, description="Filter by category"),
    status: ArticleStatus = Query(None, description="Filter by article status"),
    user_id: int = Query(None, description="Filter by user ID"),
    limit: int = Query(10, description="Number of articles per page"),
    offset: int = Query(0, description="Offset for pagination")
):
    """ Retrieve a list of articles with optional filtering and pagination. """
    return get_articles(
        db, 
        user=user,  
        title=title, 
        tag=tag, 
        category=category, 
        status=status, 
        user_id=user_id, 
        limit=limit, 
        offset=offset
    )

# Get a single article (Anyone can view)
@router.get("/{id}", response_model=ArticleResponse)
def read_article(id: int, db: Session = Depends(get_db)):
    """ Retrieve a single article by ID. """
    article = get_article(db, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

# Update an article (Admin, Author only)
@router.put("/{id}", response_model=ArticleResponse)
def update_existing_article(
    id: int, 
    article: ArticleUpdate, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Update an article. Only admins & authors (own articles) can edit. """
    db_article = get_article(db, id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    if user.role != UserRole.admin and db_article.user_id != user.id:  
        raise HTTPException(status_code=403, detail="You can only update your own articles")

    return update_article(db, id, article, user.id)

# Delete an article (Admin & Author of the article)
@router.delete("/{id}")
def delete_existing_article(
    id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Delete an article. Authors can delete their own articles; admins can delete any article. """
    db_article = get_article(db, id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    if user.role != UserRole.admin and db_article.user_id != user.id:  
        raise HTTPException(status_code=403, detail="You can only delete your own articles")

    if delete_article(db, id, user.id):
        return {"detail": "Article deleted successfully"}

# Like an article (Anyone)
@router.post("/{id}/like")
def like_post(
    id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Like an article. """
    return like_article(db, id, user.id)

# Unlike an article (Anyone)
@router.post("/{id}/unlike")
def unlike_post(
    id: int, 
    db: Session = Depends(get_db), 
    user: UserDB = Depends(get_current_user)
):
    """ Unlike an article. """
    return unlike_article(db, id, user.id)

# Get article likes count (Anyone)
@router.get("/{id}/likes")
def get_likes(id: int, db: Session = Depends(get_db)):
    """ Get the number of likes for an article. """
    return {"likes": get_article_likes(db, id)}
