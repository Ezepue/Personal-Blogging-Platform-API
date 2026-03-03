"""
Article CRUD tests including role-based write access.

Key regression: READERs must NOT be able to create articles (was a bug).
"""
import pytest
from tests.conftest import make_user, auth_header, make_article
from models.enums import UserRole


# ── Create ────────────────────────────────────────────────────────────────────

def test_author_can_create_article(client, db):
    author = make_user(db, "author1", role=UserRole.AUTHOR)
    res = client.post("/articles/", json={
        "title": "A Proper Article",
        "content": "This has enough content to pass validation.",
        "tags": ["tech"],
    }, headers=auth_header(author))
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "A Proper Article"
    assert data["author_id"] == author.id


def test_admin_can_create_article(client, db):
    admin = make_user(db, "admin1", role=UserRole.ADMIN)
    res = client.post("/articles/", json={
        "title": "Admin Article Here",
        "content": "Written by an admin user, should be allowed.",
        "tags": [],
    }, headers=auth_header(admin))
    assert res.status_code == 200


def test_super_admin_can_create_article(client, db):
    sa = make_user(db, "superadmin1", role=UserRole.SUPER_ADMIN)
    res = client.post("/articles/", json={
        "title": "Super Admin Article",
        "content": "Super admins should also be able to write articles.",
        "tags": [],
    }, headers=auth_header(sa))
    assert res.status_code == 200


def test_reader_cannot_create_article(client, db):
    """REGRESSION: READERs were previously able to post — must return 403."""
    reader = make_user(db, "reader1", role=UserRole.READER)
    res = client.post("/articles/", json={
        "title": "Reader Sneaky Post",
        "content": "A reader trying to post should be blocked.",
        "tags": [],
    }, headers=auth_header(reader))
    assert res.status_code == 403
    assert "author" in res.json()["detail"].lower()


def test_unauthenticated_cannot_create_article(client):
    res = client.post("/articles/", json={
        "title": "No Auth Article",
        "content": "Should fail without a token.",
        "tags": [],
    })
    assert res.status_code == 401


def test_create_article_title_too_short(client, db):
    author = make_user(db, "author2", role=UserRole.AUTHOR)
    res = client.post("/articles/", json={
        "title": "Hi",     # 2 chars — Pydantic schema has min_length=3 → 422
        "content": "Long enough content here.",
        "tags": [],
    }, headers=auth_header(author))
    # ArticleCreate schema enforces min_length=3 at the Pydantic layer (422),
    # so the route's own 400 check (len < 5) is never reached.
    assert res.status_code == 422


def test_create_article_content_too_short(client, db):
    author = make_user(db, "author3", role=UserRole.AUTHOR)
    res = client.post("/articles/", json={
        "title": "Valid Title",
        "content": "Short",    # 5 chars — Pydantic min_length=10 → 422
        "tags": [],
    }, headers=auth_header(author))
    assert res.status_code == 422


def test_create_duplicate_title_rejected(client, db):
    author = make_user(db, "author4", role=UserRole.AUTHOR)
    payload = {"title": "Unique Title Here", "content": "Long enough content.", "tags": []}
    client.post("/articles/", json=payload, headers=auth_header(author))
    res = client.post("/articles/", json=payload, headers=auth_header(author))
    assert res.status_code == 400


# ── Read ──────────────────────────────────────────────────────────────────────

def test_list_articles_empty(client):
    res = client.get("/articles/")
    assert res.status_code == 200
    assert res.json() == []


def test_list_articles_returns_created(client, db):
    author = make_user(db, "author5", role=UserRole.AUTHOR)
    make_article(client, author, title="Listed Article")
    res = client.get("/articles/")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_article_by_id(client, db):
    author = make_user(db, "author6", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Readable Article")
    res = client.get(f"/articles/{article['id']}")
    assert res.status_code == 200
    assert res.json()["title"] == "Readable Article"


def test_get_nonexistent_article(client):
    res = client.get("/articles/9999")
    assert res.status_code == 404


def test_search_articles_by_title(client, db):
    author = make_user(db, "author7", role=UserRole.AUTHOR)
    make_article(client, author, title="Python Is Awesome")
    make_article(client, author, title="JavaScript Tips and Tricks")
    res = client.get("/articles/?search=python")
    assert res.status_code == 200
    results = res.json()
    assert len(results) == 1
    assert "Python" in results[0]["title"]


def test_list_articles_pagination(client, db):
    author = make_user(db, "author8", role=UserRole.AUTHOR)
    for i in range(5):
        make_article(client, author, title=f"Article Number {i} Title")
    res = client.get("/articles/?limit=3&skip=0")
    assert res.status_code == 200
    assert len(res.json()) == 3


# ── Update ────────────────────────────────────────────────────────────────────

def test_author_can_update_own_article(client, db):
    author = make_user(db, "author9", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Original Title Here")
    res = client.put(f"/articles/{article['id']}", json={
        "title": "Updated Title Here",
        "content": "Updated content that is long enough.",
    }, headers=auth_header(author))
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Title Here"


def test_author_cannot_update_others_article(client, db):
    owner = make_user(db, "owner1", role=UserRole.AUTHOR)
    intruder = make_user(db, "intruder1", role=UserRole.AUTHOR)
    article = make_article(client, owner, title="Owners Article Title")
    res = client.put(f"/articles/{article['id']}", json={
        "title": "Hijacked Title Here",
        "content": "Intruder trying to update someone elses article.",
    }, headers=auth_header(intruder))
    assert res.status_code == 403


def test_admin_can_update_any_article(client, db):
    author = make_user(db, "author10", role=UserRole.AUTHOR)
    admin = make_user(db, "admin2", role=UserRole.ADMIN)
    article = make_article(client, author, title="Authors Article Title")
    res = client.put(f"/articles/{article['id']}", json={
        "title": "Admin Edited Title",
        "content": "Admin has the right to edit any article.",
    }, headers=auth_header(admin))
    assert res.status_code == 200


def test_update_nonexistent_article(client, db):
    author = make_user(db, "author11", role=UserRole.AUTHOR)
    res = client.put("/articles/9999", json={
        "title": "Does Not Matter",
        "content": "Will not be created either.",
    }, headers=auth_header(author))
    assert res.status_code == 404


def test_reader_cannot_update_article(client, db):
    author = make_user(db, "author12", role=UserRole.AUTHOR)
    reader = make_user(db, "reader2", role=UserRole.READER)
    article = make_article(client, author, title="Protected Article Title")
    res = client.put(f"/articles/{article['id']}", json={
        "title": "Readers Sneaky Edit",
        "content": "Readers should not be allowed to edit articles.",
    }, headers=auth_header(reader))
    assert res.status_code == 403


# ── Delete ────────────────────────────────────────────────────────────────────

def test_author_can_delete_own_article(client, db):
    author = make_user(db, "author13", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Article To Delete Now")
    res = client.delete(f"/articles/{article['id']}", headers=auth_header(author))
    assert res.status_code == 200


def test_author_cannot_delete_others_article(client, db):
    owner = make_user(db, "owner2", role=UserRole.AUTHOR)
    thief = make_user(db, "thief1", role=UserRole.AUTHOR)
    article = make_article(client, owner, title="Protected Article Delete")
    res = client.delete(f"/articles/{article['id']}", headers=auth_header(thief))
    assert res.status_code == 403


def test_admin_can_delete_any_article(client, db):
    author = make_user(db, "author14", role=UserRole.AUTHOR)
    admin = make_user(db, "admin3", role=UserRole.ADMIN)
    article = make_article(client, author, title="Article Admin Deletes")
    res = client.delete(f"/articles/{article['id']}", headers=auth_header(admin))
    assert res.status_code == 200


def test_unauthenticated_cannot_delete_article(client, db):
    author = make_user(db, "author15", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Article Nobody Deletes")
    res = client.delete(f"/articles/{article['id']}")
    assert res.status_code == 401
