from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models.user import User

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
USERNAME = "an.nguyen"
PASSWORD = "matkhau12345"
WRONG = "sai-mat-khau-123"
LOCKED_MSG = "Dang nhap sai qua nhieu lan, thu lai sau 15 phut"


def register(client):
    res = client.post(REGISTER, json={
        "username": USERNAME, "email": "an.nguyen@example.com", "password": PASSWORD,
        "full_name": "Nguyen Van An", "phone": "0901234567",
    })
    assert res.status_code == 201


def login(client, password, login_name=USERNAME):
    return client.post(LOGIN, json={"login": login_name, "password": password})


def get_user(db):
    db.expire_all()
    return db.scalar(select(User).where(User.username == USERNAME))


def fail(client, times):
    for _ in range(times):
        assert login(client, WRONG).status_code == 401


def test_four_failures_not_locked(client, db):
    register(client)
    fail(client, 4)
    assert login(client, PASSWORD).status_code == 200
    assert get_user(db).failed_login_count == 0


def test_five_failures_locks_account(client, db):
    register(client)
    fail(client, 5)
    res = login(client, PASSWORD)  # dung mat khau van bi chan
    assert res.status_code == 429
    assert res.json()["detail"] == LOCKED_MSG
    user = get_user(db)
    assert user.locked_until is not None
    remaining = user.locked_until - datetime.now(UTC)
    assert timedelta(minutes=14) < remaining <= timedelta(minutes=15)


def test_lock_counts_email_and_username_together(client):
    register(client)
    fail(client, 3)
    for _ in range(2):
        assert login(client, WRONG, "an.nguyen@example.com").status_code == 401
    assert login(client, PASSWORD).status_code == 429


def test_lock_expires(client, db):
    register(client)
    fail(client, 5)
    user = get_user(db)
    user.locked_until = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    assert login(client, PASSWORD).status_code == 200
    user = get_user(db)
    assert user.locked_until is None
    assert user.failed_login_count == 0


def test_failures_outside_window_not_counted(client, db):
    register(client)
    fail(client, 4)
    user = get_user(db)
    user.failed_login_started_at = datetime.now(UTC) - timedelta(minutes=16)
    db.commit()
    assert login(client, WRONG).status_code == 401  # lan sai moi -> dem lai tu 1
    user = get_user(db)
    assert user.failed_login_count == 1
    assert user.locked_until is None


def test_attempts_while_locked_do_not_extend(client, db):
    register(client)
    fail(client, 5)
    locked_until = get_user(db).locked_until
    assert login(client, WRONG).status_code == 429
    assert get_user(db).locked_until == locked_until


def test_unknown_account_not_counted(client):
    for _ in range(10):
        assert login(client, PASSWORD, "khongco").status_code == 401
