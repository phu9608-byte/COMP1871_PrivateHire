import pytest
from sqlalchemy import select

from app.models.user import User

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"

USERNAME = "an.nguyen"
PASSWORD = "matkhau12345"
WRONG_LOGIN = "Thong tin dang nhap khong dung"


def register(client, **overrides):
    data = {
        "username": USERNAME,
        "email": "an.nguyen@example.com",
        "password": PASSWORD,
        "full_name": "Nguyen Van An",
        "phone": "0901234567",
    }
    data.update(overrides)
    res = client.post(REGISTER, json=data)
    assert res.status_code == 201
    return res.json()


def deactivate(db):
    user = db.scalar(select(User).where(User.username == USERNAME))
    user.is_active = False
    db.commit()


def test_login_success(client):
    register(client)
    res = client.post(LOGIN, json={"login": USERNAME, "password": PASSWORD})
    assert res.status_code == 200
    user = res.json()["user"]
    assert user["username"] == USERNAME
    assert "password_hash" not in user and "password" not in user


def test_login_with_username(client):
    register(client)
    res = client.post(LOGIN, json={"login": " An.Nguyen ", "password": PASSWORD})
    assert res.status_code == 200
    assert res.json()["user"]["username"] == USERNAME


def test_login_with_email(client):
    register(client)
    res = client.post(LOGIN, json={"login": "An.Nguyen@Example.com", "password": PASSWORD})
    assert res.status_code == 200
    assert res.json()["user"]["username"] == USERNAME


def test_login_wrong_password_with_email(client):
    register(client)
    res = client.post(LOGIN, json={"login": "an.nguyen@example.com", "password": "sai-mat-khau-123"})
    assert res.status_code == 401
    assert res.json()["detail"] == WRONG_LOGIN


def test_password_spaces_preserved(client):
    # Password manager / dan mat khau: khong duoc cat khoang trang (AC 6)
    register(client, password="  matkhau12345  ")
    assert client.post(LOGIN, json={"login": USERNAME, "password": "  matkhau12345  "}).status_code == 200
    assert client.post(LOGIN, json={"login": USERNAME, "password": "matkhau12345"}).status_code == 401


def test_login_wrong_password(client):
    register(client)
    res = client.post(LOGIN, json={"login": USERNAME, "password": "sai-mat-khau-123"})
    assert res.status_code == 401
    assert res.json()["detail"] == WRONG_LOGIN


def test_login_unknown_username(client):
    res = client.post(LOGIN, json={"login": "khongco", "password": PASSWORD})
    assert res.status_code == 401
    assert res.json()["detail"] == WRONG_LOGIN


def test_login_inactive_user(client, db):
    register(client)
    deactivate(db)
    res = client.post(LOGIN, json={"login": USERNAME, "password": PASSWORD})
    assert res.status_code == 403
    assert res.json()["detail"] == "Tai khoan da bi khoa"


def test_login_inactive_user_wrong_password_is_401(client, db):
    # Sai mat khau thi khong duoc biet tai khoan co bi khoa hay khong
    register(client)
    deactivate(db)
    res = client.post(LOGIN, json={"login": USERNAME, "password": "sai-mat-khau-123"})
    assert res.status_code == 401


@pytest.mark.parametrize(
    "body",
    [
        {"login": USERNAME},                                # thieu password
        {"password": PASSWORD},                             # thieu login
        {"login": USERNAME, "password": PASSWORD, "x": 1},  # truong la
        {"username": USERNAME, "password": PASSWORD},       # sai ten truong
    ],
)
def test_login_invalid_body(client, body):
    assert client.post(LOGIN, json=body).status_code == 422


def test_logout_returns_204(client):
    res = client.post(LOGOUT)
    assert res.status_code == 204
    assert res.content == b""
