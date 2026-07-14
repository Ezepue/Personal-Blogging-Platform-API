"""RSS feed and sitemap endpoints (mounted at the app root)."""
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import FRONTEND_URL
from app.models.article import ArticleDB
from app.models.enums import ArticleStatus
from app.utils.text import strip_html

router = APIRouter()


def _published(db: Session, limit: int = 50):
    return (
        db.query(ArticleDB)
        .filter(ArticleDB.status == ArticleStatus.PUBLISHED, ArticleDB.is_unlisted == False)
        .order_by(ArticleDB.published_date.desc().nulls_last(), ArticleDB.id.desc())
        .limit(limit)
        .all()
    )


@router.get("/rss.xml", include_in_schema=False)
def rss_feed(db: Session = Depends(get_db)):
    """RSS 2.0 feed of the latest published articles."""
    items = []
    for a in _published(db, limit=30):
        link = f"{FRONTEND_URL}/posts/{a.id}"
        description = escape((a.subtitle or strip_html(a.content))[:300].strip())
        pub = a.published_date.strftime("%a, %d %b %Y %H:%M:%S GMT") if a.published_date else ""
        items.append(
            f"<item><title>{escape(a.title)}</title>"
            f"<link>{link}</link><guid>{link}</guid>"
            f"<description>{description}</description>"
            f"<pubDate>{pub}</pubDate></item>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        "<title>Quill — Personal Blogging Platform</title>"
        f"<link>{FRONTEND_URL}</link>"
        "<description>Latest stories from Quill</description>"
        f'{"".join(items)}'
        "</channel></rss>"
    )
    return Response(content=xml, media_type="application/rss+xml")


@router.get("/rss/{username}.xml", include_in_schema=False)
def author_rss_feed(username: str, db: Session = Depends(get_db)):
    """RSS 2.0 feed of one writer's published stories."""
    from app.models.user import UserDB

    user = db.query(UserDB).filter(UserDB.username == username, UserDB.is_active == True).first()
    if user is None:
        return Response(status_code=404)

    items = []
    rows = (
        db.query(ArticleDB)
        .filter(
            ArticleDB.status == ArticleStatus.PUBLISHED,
            ArticleDB.is_unlisted == False,
            ArticleDB.author_id == user.id,
        )
        .order_by(ArticleDB.published_date.desc().nulls_last(), ArticleDB.id.desc())
        .limit(30)
        .all()
    )
    for a in rows:
        link = f"{FRONTEND_URL}/posts/{a.id}"
        description = escape((a.subtitle or strip_html(a.content))[:300].strip())
        pub = a.published_date.strftime("%a, %d %b %Y %H:%M:%S GMT") if a.published_date else ""
        items.append(
            f"<item><title>{escape(a.title)}</title>"
            f"<link>{link}</link><guid>{link}</guid>"
            f"<description>{description}</description>"
            f"<pubDate>{pub}</pubDate></item>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        f"<title>{escape(username)} — Quill</title>"
        f"<link>{FRONTEND_URL}/profile/{escape(username)}</link>"
        f"<description>Stories by {escape(username)}</description>"
        f'{"".join(items)}'
        "</channel></rss>"
    )
    return Response(content=xml, media_type="application/rss+xml")


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap(db: Session = Depends(get_db)):
    """Sitemap of the public site: home plus all published posts."""
    urls = [f"<url><loc>{FRONTEND_URL}/</loc></url>"]
    for a in _published(db, limit=1000):
        lastmod = ""
        if a.updated_date:
            lastmod = f"<lastmod>{a.updated_date.date().isoformat()}</lastmod>"
        urls.append(f"<url><loc>{FRONTEND_URL}/posts/{a.id}</loc>{lastmod}</url>")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{"".join(urls)}'
        "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")
