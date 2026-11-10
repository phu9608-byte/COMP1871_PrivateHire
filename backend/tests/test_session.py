from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models import User, UserSession
from app.services import auth_service

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/auth/me"
USERNAME = "an.nguyen"
PASSWORD = "matkhau12345"
NOT_LOGGED_IN = "Chua dang nhap hoac phien da het han"


def register(client):
    res = client.post(REGISTER, json={
        "username": USERNAME, "email": "an.nguyen@example.com", "password": PASSWORD,
        "full_name": "Nguyen Van An", "phone": "0901234567",
    })
    assert res.status_code == 201


def login(client):
    res = client.post(LOGIN, json={"login": USERNAME, "password": PASSWORD})
    assert res.status_code == 200
    return res


def session_count(db):
    db.expire_all()
    return db.scalar(select(func.count()).select_from(UserSession))


def me_with(client, session_id):
    # Gui cookie bang tay, khong dung cookie dang luu trong client
    client.cookies.clear()
    return client.get(ME, headers={"Cookie": f"session_id={session_id}"})


def test_login_sets_secure_httponly_cookie(client, db):
    register(client)
    res = login(client)
    cookie = res.headers["set-cookie"]
    assert cookie.startswith("session_id=")
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "samesite=lax" in cookie.lower()
    session_id = client.cookies["session_id"]
    assert session_id not in res.text  # khong bao gio tra session ID trong body
    assert "no-store" in res.headers["cache-control"]
    assert session_count(db) == 1


def test_me_after_login(client):
    register(client)
    login(client)
    res = client.get(ME)
    assert res.status_code == 200
    assert res.json()["username"] == USERNAME
    assert "no-store" in res.headers["cache-control"]


def test_me_without_login(client):
    res = client.get(ME)
    assert res.status_code == 401
    assert res.json()["detail"] == NOT_LOGGED_IN


def test_me_with_bad_cookie(client):
    res = me_with(client, "rac")
    assert res.status_code == 401
    assert res.json()["detail"] == NOT_LOGGED_IN


def test_logout_ends_session(client, db):
    register(client)
    login(client)
    session_id = client.cookies["session_id"]
    res = client.post(LOGOUT)
    assert res.status_code == 204
    assert "no-store" in res.headers["cache-control"]
    assert 'session_id=""' in res.headers["set-cookie"] or "Max-Age=0" in res.headers["set-cookie"]
    assert client.get(ME).status_code == 401
    assert me_with(client, session_id).status_code == 401  # dung lai ID cu cung khong duoc
    assert session_count(db) == 0


def test_logout_without_session_is_204(client):
    assert client.post(LOGOUT).status_code == 204


def test_logout_only_this_browser(client, client2):
    register(client)
    login(client)
    login(client2)
    assert client.post(LOGOUT).status_code == 204
    assert client.get(ME).status_code == 401
    assert client2.get(ME).status_code == 200


def test_login_issues_new_session_id(client, db):
    register(client)
    login(client)
    first = client.cookies["session_id"]
    login(client)
    second = client.cookies["session_id"]
    assert first != second
    assert session_count(db) == 1  # phien cu cua trinh duyet nay da bi xoa
    assert me_with(client, first).status_code == 401
    assert me_with(client, second).status_code == 200


def _set_last_seen(db, minutes_ago):
    db.expire_all()
    s = db.scalar(select(UserSession))
    s.last_seen_at = datetime.now(UTC) - timedelta(minutes=minutes_ago)
    db.commit()


def test_session_expires_after_30_min_idle(client, db):
    register(client)
    login(client)
    _set_last_seen(db, 31)
    assert client.get(ME).status_code == 401
    assert session_count(db) == 0


def test_activity_extends_session(client, db):
    register(client)
    login(client)
    _set_last_seen(db, 29)
    assert client.get(ME).status_code == 200
    db.expire_all()
    last_seen = db.scalar(select(UserSession)).last_seen_at
    assert datetime.now(UTC) - last_seen < timedelta(seconds=30)


def test_inactive_user_session_rejected(client, db):
    register(client)
    login(client)
    db.expire_all()
    user = db.scalar(select(User).where(User.username == USERNAME))
    user.is_active = False
    db.commit()
    assert client.get(ME).status_code == 401


def test_delete_all_sessions(client, db):
    register(client)
    browsers = [TestClient(app, base_url="https://testserver") for _ in range(3)]
    for b in browsers:
        login(b)
    user = db.scalar(select(User).where(User.username == USERNAME))
    assert auth_service.delete_all_sessions(db, user.id) == 3
    for b in browsers:
        assert b.get(ME).status_code == 401


def test_delete_user_deletes_sessions(client, db):
    register(client)
    login(client)
    user = db.scalar(select(User).where(User.username == USERNAME))
    db.delete(user)
    db.commit()
    assert session_count(db) == 0
