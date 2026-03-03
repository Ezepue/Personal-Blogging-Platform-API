"""
Dedicated role-based access control (RBAC) matrix tests.

Tests every role against every protected action to ensure the permission
matrix is enforced end-to-end. This is the file that catches the class of
bug where a READER could write posts.
"""
import pytest
from tests.conftest import make_user, auth_header, make_article
from models.enums import UserRole


# ── Helpers ───────────────────────────────────────────────────────────────────

def _post_article(client, user, title="RBAC Article Title Test"):
    return client.post("/articles/", json={
        "title": title,
        "content": "Content long enough to pass the 10-char check.",
        "tags": [],
    }, headers=auth_header(user))


def _put_article(client, user, article_id):
    return client.put(f"/articles/{article_id}", json={
        "title": "RBAC Updated Title",
        "content": "Updated content for RBAC testing purposes here.",
    }, headers=auth_header(user))


def _delete_article(client, user, article_id):
    return client.delete(f"/articles/{article_id}", headers=auth_header(user))


# ── Write access matrix ───────────────────────────────────────────────────────

def test_reader_blocked_from_writing(client, db):
    """READER role must be blocked on all write operations."""
    reader = make_user(db, "reader1", role=UserRole.READER)
    author_seed = make_user(db, "owner1", role=UserRole.AUTHOR)
    article = make_article(client, author_seed, title="Pre-Existing Article Title")

    assert _post_article(client, reader, "Reader Write Attempt").status_code == 403
    assert _put_article(client, reader, article["id"]).status_code == 403
    assert _delete_article(client, reader, article["id"]).status_code == 403


def test_author_allowed_on_own_content(client, db):
    author = make_user(db, "author1", role=UserRole.AUTHOR)
    article = make_article(client, author, title="Author Own Article Test")

    assert _put_article(client, author, article["id"]).status_code == 200
    assert _delete_article(client, author, article["id"]).status_code == 200


def test_author_blocked_on_others_content(client, db):
    owner = make_user(db, "owner2", role=UserRole.AUTHOR)
    intruder = make_user(db, "intruder1", role=UserRole.AUTHOR)
    article = make_article(client, owner, title="Owners Exclusive Article Title")

    assert _put_article(client, intruder, article["id"]).status_code == 403
    assert _delete_article(client, intruder, article["id"]).status_code == 403


def test_admin_allowed_on_any_content(client, db):
    author = make_user(db, "author2", role=UserRole.AUTHOR)
    admin = make_user(db, "admin1", role=UserRole.ADMIN)
    article1 = make_article(client, author, title="Content Admin Can Edit")
    article2 = make_article(client, author, title="Content Admin Can Delete")

    assert _put_article(client, admin, article1["id"]).status_code == 200
    assert _delete_article(client, admin, article2["id"]).status_code == 200


def test_super_admin_allowed_on_any_content(client, db):
    author = make_user(db, "author3", role=UserRole.AUTHOR)
    sa = make_user(db, "sa1", role=UserRole.SUPER_ADMIN)
    article = make_article(client, author, title="Super Admin Editable Article")

    assert _put_article(client, sa, article["id"]).status_code == 200


# ── Admin route access matrix ─────────────────────────────────────────────────

@pytest.mark.parametrize("role,expected", [
    (UserRole.READER,      403),
    (UserRole.AUTHOR,      403),
    (UserRole.ADMIN,       403),     # admin route for /users is SUPER_ADMIN only
    (UserRole.SUPER_ADMIN, 200),
])
def test_admin_users_endpoint_role_matrix(client, db, role, expected):
    user = make_user(db, f"u_{role.value}", role=role)
    res = client.get("/admin/users", headers=auth_header(user))
    assert res.status_code == expected, \
        f"{role.value} got {res.status_code}, expected {expected}"


@pytest.mark.parametrize("role,expected", [
    (UserRole.READER,      403),
    (UserRole.AUTHOR,      403),
    (UserRole.ADMIN,       200),
    (UserRole.SUPER_ADMIN, 200),
])
def test_admin_articles_endpoint_role_matrix(client, db, role, expected):
    user = make_user(db, f"ua_{role.value}", role=role)
    res = client.get("/admin/articles", headers=auth_header(user))
    assert res.status_code == expected, \
        f"{role.value} got {res.status_code}, expected {expected}"


@pytest.mark.parametrize("role,expected", [
    (UserRole.READER,      403),
    (UserRole.AUTHOR,      403),
    (UserRole.ADMIN,       200),
    (UserRole.SUPER_ADMIN, 200),
])
def test_admin_comments_endpoint_role_matrix(client, db, role, expected):
    user = make_user(db, f"uc_{role.value}", role=role)
    res = client.get("/admin/comments", headers=auth_header(user))
    assert res.status_code == expected, \
        f"{role.value} got {res.status_code}, expected {expected}"


# ── Create article matrix ─────────────────────────────────────────────────────

@pytest.mark.parametrize("role,expected", [
    (UserRole.READER,      403),   # <-- this is the bug that was fixed
    (UserRole.AUTHOR,      200),
    (UserRole.ADMIN,       200),
    (UserRole.SUPER_ADMIN, 200),
])
def test_create_article_role_matrix(client, db, role, expected):
    user = make_user(db, f"ca_{role.value}", role=role)
    res = _post_article(client, user, title=f"Matrix Article For {role.value}")
    assert res.status_code == expected, \
        f"{role.value} got {res.status_code}, expected {expected}"


# ── Comment access matrix ─────────────────────────────────────────────────────

@pytest.mark.parametrize("role", [
    UserRole.READER,
    UserRole.AUTHOR,
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN,
])
def test_all_roles_can_comment(client, db, role):
    """Any authenticated user can leave comments regardless of role."""
    seed_author = make_user(db, "seed_author", role=UserRole.AUTHOR)
    article = make_article(client, seed_author, title="Open Comments Article Title")

    user = make_user(db, f"commenter_{role.value}", role=role)
    res = client.post("/comments/", json={
        "article_id": article["id"],
        "content": "Testing that all roles can comment freely.",
    }, headers=auth_header(user))
    assert res.status_code == 200, \
        f"{role.value} should be able to comment, got {res.status_code}"
