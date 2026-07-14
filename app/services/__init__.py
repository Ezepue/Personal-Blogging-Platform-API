"""Service layer: business logic grouped by domain.

Routers depend on these functions rather than writing queries inline, keeping
HTTP concerns and domain rules separate. The aggregate re-exports below give
routers a single stable import surface.
"""
from app.services.articles import (  # noqa: F401
    can_view_article,
    create_new_article,
    delete_article,
    get_article_by_id,
    get_article_with_likes,
    get_articles,
    get_user_drafts,
    update_article,
)
from app.services.comments import (  # noqa: F401
    create_new_comment,
    delete_comment,
    extract_mentions,
    get_all_comments,
    get_comment_by_id,
    get_comments_by_article,
)
from app.services.users import (  # noqa: F401
    create_new_user,
    delete_user_from_db,
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    promote_user,
    update_user_profile,
    update_user_role,
)
