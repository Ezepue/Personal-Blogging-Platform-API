"""
Comment CRUD tests: creation, listing, deletion, permission checks.
"""
import pytest
from tests.conftest import make_user, auth_header, make_article
from models.enums import UserRole


def _make_comment(client, user, article_id, content="This is a test comment body."):
    res = client.post("/comments/", json={
        "article_id": article_id,
        "content": content,
    }, headers=auth_header(user))
    return res


# ── Create ────────────────────────────────────────────────────────────────────

def test_any_authenticated_user_can_comment(client, db):
    author = make_user(db, "author1", role=UserRole.AUTHOR)
    reader = make_user(db, "reader1", role=UserRole.READER)
    article = make_article(client, author, title="Commentable Article Title")

    res = _make_comment(client, reader, article["id"])
    assert res.status_code == 200
    assert "id" in res.json()


def test_unauthenticated_cannot_comment(client, db):
    author = make_user(db, "author2", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Protected Comment Article")
    res = client.post("/comments/", json={
        "article_id": article["id"],
        "content": "Sneaky anon comment.",
    })
    assert res.status_code == 401


def test_comment_on_nonexistent_article(client, db):
    reader = make_user(db, "reader2", role=UserRole.READER)
    res = _make_comment(client, reader, article_id=9999)
    assert res.status_code == 404


# ── Read ──────────────────────────────────────────────────────────────────────

def test_list_comments_empty(client, db):
    author = make_user(db, "author3", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Article With No Comments")
    res = client.get(f"/comments/{article['id']}")
    assert res.status_code == 200
    assert res.json() == []


def test_list_comments_returns_all(client, db):
    author = make_user(db, "author4", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter1", role=UserRole.READER)
    article = make_article(client, author, title="Busy Comment Article Title")

    for i in range(3):
        _make_comment(client, commenter, article["id"], content=f"Comment number {i} body text.")

    res = client.get(f"/comments/{article['id']}")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_list_comments_includes_user_info(client, db):
    """Comments should include nested user object (not just user_id)."""
    author = make_user(db, "author5", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter2", role=UserRole.READER)
    article = make_article(client, author, title="Comment User Info Article")
    _make_comment(client, commenter, article["id"])

    res = client.get(f"/comments/{article['id']}")
    comment = res.json()[0]
    assert "user" in comment
    assert comment["user"]["username"] == "commenter2"


# ── Delete ────────────────────────────────────────────────────────────────────

def test_user_can_delete_own_comment(client, db):
    author = make_user(db, "author6", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter3", role=UserRole.READER)
    article = make_article(client, author, title="Delete Own Comment Article")
    comment = _make_comment(client, commenter, article["id"]).json()

    res = client.delete(f"/comments/{comment['id']}", headers=auth_header(commenter))
    assert res.status_code == 200


def test_user_cannot_delete_others_comment(client, db):
    author = make_user(db, "author7", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter4", role=UserRole.READER)
    intruder = make_user(db, "intruder1", role=UserRole.READER)
    article = make_article(client, author, title="Protected Comment Article Two")
    comment = _make_comment(client, commenter, article["id"]).json()

    res = client.delete(f"/comments/{comment['id']}", headers=auth_header(intruder))
    assert res.status_code == 403


def test_article_author_can_delete_comment_on_own_article(client, db):
    """Article authors can moderate comments on their own posts."""
    article_author = make_user(db, "author8", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter5", role=UserRole.READER)
    article = make_article(client, article_author, title="Moderated Comments Article")
    comment = _make_comment(client, commenter, article["id"]).json()

    res = client.delete(f"/comments/{comment['id']}", headers=auth_header(article_author))
    assert res.status_code == 200


def test_admin_can_delete_any_comment(client, db):
    author = make_user(db, "author9", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter6", role=UserRole.READER)
    admin = make_user(db, "admin1", role=UserRole.ADMIN)
    article = make_article(client, author, title="Admin Moderated Article")
    comment = _make_comment(client, commenter, article["id"]).json()

    res = client.delete(f"/admin/comments/{comment['id']}", headers=auth_header(admin))
    assert res.status_code == 200


def test_unauthenticated_cannot_delete_comment(client, db):
    author = make_user(db, "author10", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter7", role=UserRole.READER)
    article = make_article(client, author, title="Unprotected Comment Article")
    comment = _make_comment(client, commenter, article["id"]).json()

    res = client.delete(f"/comments/{comment['id']}")
    assert res.status_code == 401


def test_delete_nonexistent_comment(client, db):
    reader = make_user(db, "reader1", role=UserRole.READER)
    res = client.delete("/comments/9999", headers=auth_header(reader))
    assert res.status_code == 404
