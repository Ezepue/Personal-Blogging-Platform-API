import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserResponse, UserProfileUpdate, UserPasswordChange, UserPublicProfile,
    NotificationPrefs, FollowUserEntry, AccountDelete,
)
from app.schemas.article import ArticleResponse
from app.schemas.token import RefreshTokenResponse
from app.models.view_history import ViewHistoryDB
from app.services import delete_user_from_db, get_user_drafts
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional
from app.api.deps import (
    create_access_token, get_current_user, get_optional_user, hash_password, verify_password,
    verify_user_credentials, create_refresh_token, verify_refresh_token, create_ws_ticket
)
from app.services import create_new_user, get_user_by_username, update_user_profile
from app.utils.file_validation import is_valid_image
from app.services.notifications import send_notification_to_user
from app.models.user import UserDB, UserRole
from app.models.article import ArticleDB
from app.models.follow import FollowDB
from app.models.enums import ArticleStatus
from app.models.refresh_token import RefreshTokenDB
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, UPLOAD_FOLDER

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_new_user(db, user, role=UserRole.READER)

    logger.info(f"New user registered: {new_user.username} ({new_user.email})")
    return new_user

@router.post("/login")
@limiter.limit("3/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT access and refresh tokens."""
    user = verify_user_credentials(db, form_data.username, form_data.password)
    if user is None:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(user.id, db)

    logger.info(f"User {user.username} logged in successfully.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    user_id = verify_refresh_token(refresh_token, db)
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(
        {"sub": str(user_id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"Access token refreshed for user {user_id}")
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Logout by revoking the user's active refresh tokens. Idempotent."""
    try:
        db.query(RefreshTokenDB).filter_by(user_id=current_user.id, is_active=True).update(
            {"is_active": False, "revoked": True}
        )
        db.commit()
        return {"detail": "Logged out successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Logout failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")


@router.get("/ws-ticket")
def get_ws_ticket(current_user: UserDB = Depends(get_current_user)):
    """Issue a short-lived, single-purpose ticket for authenticating a WebSocket handshake.

    The long-lived access token is never exposed to client-side JavaScript; the browser
    requests one of these tickets (valid for seconds) right before opening the socket.
    """
    return {"ticket": create_ws_ticket(current_user.id)}

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.username and data.username != current_user.username:
        existing = get_user_by_username(db, data.username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")
    if data.email and data.email != current_user.email:
        existing_email = db.query(UserDB).filter(UserDB.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=409, detail="Email already in use")
    updated = update_user_profile(db, current_user, data.model_dump(exclude_none=True))
    return updated

@router.put("/me/password")
async def change_password(
    data: UserPasswordChange,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only image files are allowed for avatars")
    safe_name = os.path.basename(file.filename or "upload")
    filename = f"avatar_{current_user.id}_{safe_name}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.abspath(path).startswith(os.path.abspath(UPLOAD_FOLDER)):
        raise HTTPException(status_code=400, detail="Invalid filename")
    MAX_AVATAR_SIZE = 10 * 1024 * 1024  # 10MB
    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
    # Verify the bytes are actually an image, not a mislabeled payload.
    if not is_valid_image(contents):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")
    with open(path, "wb") as f:
        f.write(contents)
    avatar_url = f"/media/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/notification-prefs", response_model=NotificationPrefs)
async def get_notification_prefs(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.put("/me/notification-prefs", response_model=NotificationPrefs)
async def update_notification_prefs(
    prefs: NotificationPrefs,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.notify_likes = prefs.notify_likes
    current_user.notify_comments = prefs.notify_comments
    current_user.notify_follows = prefs.notify_follows
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{username}/profile", response_model=UserPublicProfile)
async def get_public_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_optional_user),
):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = UserPublicProfile.model_validate(user)
    profile.followers_count = db.query(FollowDB).filter(FollowDB.followed_id == user.id).count()
    profile.following_count = db.query(FollowDB).filter(FollowDB.follower_id == user.id).count()
    profile.articles_count = (
        db.query(ArticleDB)
        .filter(ArticleDB.author_id == user.id, ArticleDB.status == ArticleStatus.PUBLISHED)
        .count()
    )
    if current_user is not None:
        profile.is_followed_by_me = (
            db.query(FollowDB)
            .filter(FollowDB.follower_id == current_user.id, FollowDB.followed_id == user.id)
            .first()
            is not None
        )
    return profile


@router.post("/{username}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Follow another user."""
    target = get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    try:
        db.add(FollowDB(follower_id=current_user.id, followed_id=target.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already following this user")

    try:
        await send_notification_to_user(
            db=db,
            user_id=target.id,
            message=f"{current_user.username} started following you",
            notif_type="follow",
            extra_data={"follower_username": current_user.username},
        )
    except Exception:
        pass  # notification failure must not fail the follow

    followers = db.query(FollowDB).filter(FollowDB.followed_id == target.id).count()
    return {"detail": f"Now following {target.username}", "followers_count": followers}


@router.delete("/{username}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Unfollow a user."""
    target = get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    follow = db.query(FollowDB).filter(
        FollowDB.follower_id == current_user.id, FollowDB.followed_id == target.id
    ).one_or_none()
    if follow is None:
        raise HTTPException(status_code=400, detail="You are not following this user")

    db.delete(follow)
    db.commit()
    followers = db.query(FollowDB).filter(FollowDB.followed_id == target.id).count()
    return {"detail": f"Unfollowed {target.username}", "followers_count": followers}


@router.get("/{username}/followers", response_model=List[FollowUserEntry])
async def list_followers(username: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 50):
    """Users who follow the given user."""
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(100, max(1, limit))
    rows = (
        db.query(UserDB)
        .join(FollowDB, FollowDB.follower_id == UserDB.id)
        .filter(FollowDB.followed_id == user.id)
        .offset(skip).limit(limit).all()
    )
    return rows


@router.get("/{username}/following", response_model=List[FollowUserEntry])
async def list_following(username: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 50):
    """Users the given user follows."""
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(100, max(1, limit))
    rows = (
        db.query(UserDB)
        .join(FollowDB, FollowDB.followed_id == UserDB.id)
        .filter(FollowDB.follower_id == user.id)
        .offset(skip).limit(limit).all()
    )
    return rows


@router.get("/{username}/articles", response_model=List[ArticleResponse])
async def get_user_articles(
    username: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    """Return published articles for a given user (public)."""
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    articles = (
        db.query(ArticleDB)
        .filter(ArticleDB.author_id == user.id, ArticleDB.status == ArticleStatus.PUBLISHED)
        .order_by(ArticleDB.id.desc())
        .offset(skip)
        .limit(min(100, max(1, limit)))
        .all()
    )
    return articles or []


@router.put("/me/pin/{article_id}", response_model=UserPublicProfile)
async def pin_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Pin one of your own published stories to the top of your profile."""
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    if not article or article.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.status != ArticleStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Only published stories can be pinned")
    current_user.pinned_article_id = article_id
    db.commit()
    db.refresh(current_user)
    return UserPublicProfile.model_validate(current_user)


@router.delete("/me/pin", response_model=UserPublicProfile)
async def unpin_article(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Remove the pinned story from your profile."""
    current_user.pinned_article_id = None
    db.commit()
    db.refresh(current_user)
    return UserPublicProfile.model_validate(current_user)


@router.get("/me/sessions", response_model=List[RefreshTokenResponse])
async def list_my_sessions(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """The caller's active sessions (live refresh tokens), newest first."""
    return (
        db.query(RefreshTokenDB)
        .filter(RefreshTokenDB.user_id == current_user.id, RefreshTokenDB.is_active == True)
        .order_by(RefreshTokenDB.created_at.desc())
        .all()
    )


@router.delete("/me/sessions/{session_id}")
async def revoke_my_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Revoke one of the caller's own sessions."""
    token = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.id == session_id, RefreshTokenDB.user_id == current_user.id
    ).first()
    if not token:
        raise HTTPException(status_code=404, detail="Session not found")
    token.is_active = False
    token.revoked = True
    db.commit()
    return {"detail": "Session revoked"}


@router.get("/me/export")
async def export_my_data(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Export the caller's profile, stories, and comments as JSON."""
    from app.models.comment import CommentDB

    articles = db.query(ArticleDB).filter(ArticleDB.author_id == current_user.id).all()
    comments = db.query(CommentDB).filter(CommentDB.user_id == current_user.id).all()
    return {
        "profile": {
            "username": current_user.username,
            "email": current_user.email,
            "bio": current_user.bio,
            "website": current_user.website,
            "location": current_user.location,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "articles": [
            {
                "id": a.id, "title": a.title, "subtitle": a.subtitle, "content": a.content,
                "tags": a.tags, "category": a.category, "status": a.status.value,
                "published_date": a.published_date.isoformat() if a.published_date else None,
            }
            for a in articles
        ],
        "comments": [
            {
                "id": c.id, "article_id": c.article_id, "content": c.content,
                "created_date": c.created_date.isoformat() if c.created_date else None,
            }
            for c in comments
        ],
    }


@router.delete("/me")
async def delete_my_account(
    data: AccountDelete,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Delete the caller's own account (password-confirmed soft delete)."""
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    delete_user_from_db(db, current_user.id)
    return {"detail": "Account deleted"}


@router.delete("/me/avatar", response_model=UserResponse)
async def remove_avatar(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Remove the caller's avatar, reverting to the initials fallback."""
    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/history", response_model=List[ArticleResponse])
async def my_reading_history(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    limit: int = 30,
):
    """Recently viewed stories, most recent first."""
    limit = min(100, max(1, limit))
    rows = (
        db.query(ArticleDB)
        .join(ViewHistoryDB, ViewHistoryDB.article_id == ArticleDB.id)
        .filter(
            ViewHistoryDB.user_id == current_user.id,
            ArticleDB.status == ArticleStatus.PUBLISHED,
        )
        .order_by(ViewHistoryDB.viewed_at.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.delete("/me/history")
async def clear_reading_history(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Clear the caller's reading history."""
    deleted = db.query(ViewHistoryDB).filter(ViewHistoryDB.user_id == current_user.id).delete(
        synchronize_session=False
    )
    db.commit()
    return {"detail": f"Cleared {deleted} entries"}
