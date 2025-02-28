from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from schemas import ArticleCreate, ArticleUpdate, ArticleResponse
from database import get_db
from crud import create_article, get_articles, get_article, update_article, delete_article, like_article, unlike_article, get_article_likes
from auth import get_current_user

router = APIRouter()

# Create an article
@router.post("/", response_model=ArticleResponse)
def create_new_article(article: ArticleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tags = article.tags if isinstance(article.tags, list) else []
    return create_article(
        db,
        ArticleCreate(
            title=article.title,
            content=article.content,
            tags=tags,
            category=article.category,
            status=article.status  # Updated from is_published to status
        ),
        user.id
    )

# Get all articles with filters
@router.get("/", response_model=list[ArticleResponse])
def read_articles(
    db: Session = Depends(get_db),
    title: str = Query(None, description="Search by article title"),
    tag: str = Query(None, description="Filter by tag"),
    category: str = Query(None, description="Filter by category"),
    status: str = Query(None, description="Filter by article status"),  # Updated filter name
    user_id: int = Query(None, description="Filter by user ID"),
    limit: int = Query(10, description="Number of articles per page"),
    offset: int = Query(0, description="Offset for pagination")
):
    return get_articles(db, title=title, tag=tag, category=category, status=status, user_id=user_id, limit=limit, offset=offset)

# Get a single article by ID
@router.get("/{id}", response_model=ArticleResponse)
def read_article(id: int, db: Session = Depends(get_db)):
    article = get_article(db, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

# Update an article
@router.put("/{id}", response_model=ArticleResponse)
def update_existing_article(id: int, article: ArticleUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return update_article(db, id, article, user.id)

# Delete an article
@router.delete("/{id}")
def delete_existing_article(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if delete_article(db, id, user.id):
        return {"detail": "Article deleted successfully"}
    raise HTTPException(status_code=404, detail="Article not found")

# Like an article
@router.post("/{id}/like")
def like_post(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return like_article(db, id, user.id)

# Unlike an article
@router.post("/{id}/unlike")
def unlike_post(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return unlike_article(db, id, user.id)

# Get article likes count
@router.get("/{id}/likes")
def get_likes(id: int, db: Session = Depends(get_db)):
    return {"likes": get_article_likes(db, id)}
