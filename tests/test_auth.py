"""
Auth endpoint tests: registration, login, token refresh, logout, profile.
"""
import pytest
from tests.conftest import make_user, auth_header
from models.enums import UserRole


# ── Registration ──────────────────────────────────────────────────────────────

def test_register_new_user(client):
    res = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "StrongPass1!",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "READER"         # all new accounts start as READER
    assert "hashed_password" not in data    # never leak password hash


def test_register_duplicate_username(client, db):
    make_user(db, "bob")
    res = client.post("/users/register", json={
        "username": "bob",
        "email": "bob_new@example.com",
        "password": "StrongPass1!",
    })
    assert res.status_code == 400


def test_register_duplicate_email(client, db):
    make_user(db, "carol")
    res = client.post("/users/register", json={
        "username": "carol2",
        "email": "carol@test.com",
        "password": "StrongPass1!",
    })
    assert res.status_code == 400


def test_register_short_username_rejected(client):
    res = client.post("/users/register", json={
        "username": "ab",          # too short (min 3)
        "email": "ab@example.com",
        "password": "StrongPass1!",
    })
    assert res.status_code == 422


def test_register_invalid_email_rejected(client):
    res = client.post("/users/register", json={
        "username": "validuser",
        "email": "not-an-email",
        "password": "StrongPass1!",
    })
    assert res.status_code == 422


def test_register_short_password_rejected(client):
    res = client.post("/users/register", json={
        "username": "validuser",
        "email": "valid@example.com",
        "password": "short",       # min 8 chars
    })
    assert res.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_valid_credentials(client, db):
    make_user(db, "dave", password="mypassword")
    res = client.post("/users/login", data={
        "username": "dave",
        "password": "mypassword",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    make_user(db, "eve", password="rightpass")
    res = client.post("/users/login", data={
        "username": "eve",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/users/login", data={
        "username": "ghost",
        "password": "anypassword",
    })
    assert res.status_code == 401


def test_login_case_insensitive_username(client, db):
    """Login should work regardless of username case."""
    make_user(db, "frank", password="testpass")
    res = client.post("/users/login", data={
        "username": "FRANK",
        "password": "testpass",
    })
    assert res.status_code == 200


# ── /users/me ─────────────────────────────────────────────────────────────────

def test_get_me_authenticated(client, db):
    user = make_user(db, "grace")
    res = client.get("/users/me", headers=auth_header(user))
    assert res.status_code == 200
    assert res.json()["username"] == "grace"


def test_get_me_unauthenticated(client):
    res = client.get("/users/me")
    assert res.status_code == 401


def test_get_me_invalid_token(client):
    res = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401


# ── Token refresh ─────────────────────────────────────────────────────────────

def test_refresh_token(client, db):
    make_user(db, "hank", password="pass1234")
    login = client.post("/users/login", data={"username": "hank", "password": "pass1234"})
    refresh_token = login.json()["refresh_token"]

    res = client.post(f"/users/refresh?refresh_token={refresh_token}")
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_refresh_with_invalid_token(client):
    res = client.post("/users/refresh?refresh_token=faketoken")
    assert res.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout_removes_session(client, db):
    make_user(db, "iris", password="pass1234")
    login = client.post("/users/login", data={"username": "iris", "password": "pass1234"})
    token = login.json()["access_token"]

    res = client.post("/users/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "Logged out" in res.json()["detail"]


def test_logout_unauthenticated(client):
    res = client.post("/users/logout")
    assert res.status_code == 401


# ── Public profile ────────────────────────────────────────────────────────────

def test_get_public_profile(client, db):
    make_user(db, "jack")
    res = client.get("/users/jack/profile")
    assert res.status_code == 200
    assert res.json()["username"] == "jack"


def test_get_nonexistent_profile(client):
    res = client.get("/users/nobody/profile")
    assert res.status_code == 404
