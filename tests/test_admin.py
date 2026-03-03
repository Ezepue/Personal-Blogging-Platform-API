"""
Admin endpoint tests: user management, role changes, content moderation.
"""
import pytest
from tests.conftest import make_user, auth_header, make_article
from models.enums import UserRole


# ── User listing ──────────────────────────────────────────────────────────────

def test_super_admin_can_list_users(client, db):
    sa = make_user(db, "sa1", role=UserRole.SUPER_ADMIN)
    make_user(db, "user1")
    make_user(db, "user2")
    res = client.get("/admin/users", headers=auth_header(sa))
    assert res.status_code == 200
    assert len(res.json()) >= 3


def test_admin_cannot_list_users(client, db):
    admin = make_user(db, "admin1", role=UserRole.ADMIN)
    res = client.get("/admin/users", headers=auth_header(admin))
    assert res.status_code == 403


def test_author_cannot_list_users(client, db):
    author = make_user(db, "author1", role=UserRole.AUTHOR)
    res = client.get("/admin/users", headers=auth_header(author))
    assert res.status_code == 403


def test_reader_cannot_list_users(client, db):
    reader = make_user(db, "reader1", role=UserRole.READER)
    res = client.get("/admin/users", headers=auth_header(reader))
    assert res.status_code == 403


def test_unauthenticated_cannot_list_users(client):
    res = client.get("/admin/users")
    assert res.status_code == 401


# ── Role changes ──────────────────────────────────────────────────────────────

def test_super_admin_can_upgrade_reader_to_author(client, db):
    sa = make_user(db, "sa2", role=UserRole.SUPER_ADMIN)
    reader = make_user(db, "reader2", role=UserRole.READER)
    res = client.put(f"/admin/{reader.id}/role",
                     json={"new_role": "AUTHOR"},
                     headers=auth_header(sa))
    assert res.status_code == 200
    assert "AUTHOR" in res.json()["detail"]


def test_super_admin_can_promote_author_to_admin(client, db):
    sa = make_user(db, "sa3", role=UserRole.SUPER_ADMIN)
    author = make_user(db, "author2", role=UserRole.AUTHOR)
    res = client.put(f"/admin/{author.id}/role",
                     json={"new_role": "ADMIN"},
                     headers=auth_header(sa))
    assert res.status_code == 200


def test_admin_cannot_change_roles(client, db):
    admin = make_user(db, "admin2", role=UserRole.ADMIN)
    reader = make_user(db, "reader3", role=UserRole.READER)
    res = client.put(f"/admin/{reader.id}/role",
                     json={"new_role": "AUTHOR"},
                     headers=auth_header(admin))
    assert res.status_code == 403


def test_cannot_change_own_role(client, db):
    sa = make_user(db, "sa4", role=UserRole.SUPER_ADMIN)
    res = client.put(f"/admin/{sa.id}/role",
                     json={"new_role": "ADMIN"},
                     headers=auth_header(sa))
    assert res.status_code == 403


def test_cannot_demote_super_admin(client, db):
    sa1 = make_user(db, "sa5", role=UserRole.SUPER_ADMIN)
    sa2 = make_user(db, "sa6", role=UserRole.SUPER_ADMIN)
    res = client.put(f"/admin/{sa2.id}/role",
                     json={"new_role": "READER"},
                     headers=auth_header(sa1))
    assert res.status_code == 403


def test_role_change_invalid_role_rejected(client, db):
    sa = make_user(db, "sa7", role=UserRole.SUPER_ADMIN)
    user = make_user(db, "user2", role=UserRole.READER)
    res = client.put(f"/admin/{user.id}/role",
                     json={"new_role": "OVERLORD"},
                     headers=auth_header(sa))
    assert res.status_code == 422   # Pydantic rejects unknown enum value


def test_role_change_sends_new_role_not_role(client, db):
    """Regression: frontend must send 'new_role', not 'role' (old bug)."""
    sa = make_user(db, "sa8", role=UserRole.SUPER_ADMIN)
    user = make_user(db, "user3", role=UserRole.READER)
    # Sending the old wrong field name should fail
    res = client.put(f"/admin/{user.id}/role",
                     json={"role": "AUTHOR"},
                     headers=auth_header(sa))
    assert res.status_code == 422


def test_role_change_user_not_found(client, db):
    sa = make_user(db, "sa9", role=UserRole.SUPER_ADMIN)
    res = client.put("/admin/9999/role",
                     json={"new_role": "AUTHOR"},
                     headers=auth_header(sa))
    assert res.status_code == 404


# ── User deletion ─────────────────────────────────────────────────────────────

def test_super_admin_can_delete_user(client, db):
    sa = make_user(db, "sa10", role=UserRole.SUPER_ADMIN)
    target = make_user(db, "target1", role=UserRole.READER)
    res = client.delete(f"/admin/{target.id}", headers=auth_header(sa))
    assert res.status_code == 200


def test_admin_cannot_delete_user(client, db):
    admin = make_user(db, "admin3", role=UserRole.ADMIN)
    target = make_user(db, "target2", role=UserRole.READER)
    res = client.delete(f"/admin/{target.id}", headers=auth_header(admin))
    assert res.status_code == 403


def test_delete_nonexistent_user(client, db):
    sa = make_user(db, "sa11", role=UserRole.SUPER_ADMIN)
    res = client.delete("/admin/9999", headers=auth_header(sa))
    assert res.status_code == 404


# ── Article moderation ────────────────────────────────────────────────────────

def test_admin_can_list_all_articles(client, db):
    admin = make_user(db, "admin4", role=UserRole.ADMIN)
    author = make_user(db, "author3", role=UserRole.AUTHOR)
    make_article(client, author, title="Admin Visible Article One")
    make_article(client, author, title="Admin Visible Article Two")

    res = client.get("/admin/articles", headers=auth_header(admin))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_reader_cannot_list_admin_articles(client, db):
    reader = make_user(db, "reader4", role=UserRole.READER)
    res = client.get("/admin/articles", headers=auth_header(reader))
    assert res.status_code == 403


def test_admin_can_delete_any_article(client, db):
    admin = make_user(db, "admin5", role=UserRole.ADMIN)
    author = make_user(db, "author4", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Article Admin Will Remove")

    res = client.delete(f"/admin/articles/{article['id']}", headers=auth_header(admin))
    assert res.status_code == 200


# ── Comment moderation ────────────────────────────────────────────────────────

def test_admin_can_list_all_comments(client, db):
    admin = make_user(db, "admin6", role=UserRole.ADMIN)
    author = make_user(db, "author5", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter1", role=UserRole.READER)
    article = make_article(client, author, title="Heavily Commented Article Title")

    for i in range(4):
        client.post("/comments/", json={
            "article_id": article["id"],
            "content": f"Comment number {i} on the article.",
        }, headers=auth_header(commenter))

    res = client.get("/admin/comments", headers=auth_header(admin))
    assert res.status_code == 200
    assert len(res.json()) == 4


def test_admin_can_delete_any_comment(client, db):
    admin = make_user(db, "admin7", role=UserRole.ADMIN)
    author = make_user(db, "author6", role=UserRole.AUTHOR)
    commenter = make_user(db, "commenter2", role=UserRole.READER)
    article = make_article(client, author, title="Comment Moderation Article Test")
    comment = client.post("/comments/", json={
        "article_id": article["id"],
        "content": "Comment admin will delete right now.",
    }, headers=auth_header(commenter)).json()

    res = client.delete(f"/admin/comments/{comment['id']}", headers=auth_header(admin))
    assert res.status_code == 200
