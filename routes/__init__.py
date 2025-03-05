from fastapi import APIRouter
from .users import router as user_router
from .articles import router as article_router
from .comments import router as comment_router
from .admin import router as admin_router
from .media import router as media_router