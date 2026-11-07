import pytest
from sqlalchemy import select

from app.core.security import verify_password
from app.models.user import User, UserRole

URL = "/api/v1/auth/register"
PASSWORD = "matkhau12345"  # 12 ky tu


def payload(**overrides):
    data = {
        "username": "an.nguyen",
        "email": "an.nguyen@example.com",
        "password": PASSWORD,
        "full_name": "Nguyen Van An",
        "phone": "0901234567",
    }
    data.update(overrides)
    return data


def test_register_customer_by_default(client, db):
    res = client.post(URL, json=payload())
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "an.nguyen"
    assert body["email"] == "an.nguyen@example.com"
    assert body["role"] == "customer"
    assert body["is_active"] is True
    assert body["marketing_consent"] is False  # mac dinh khong tick
    assert "password" not in body and "password_hash" not in body

    user = db.scalar(select(User).where(User.username == "an.nguyen"))
    assert user is not None
    assert user.password_hash != PASSWORD
    assert verify_password(PASSWORD, user.password_hash)


def test_register_with_marketing_consent(client):
    res = client.post(URL, json=payload(marketing_consent=True))
    assert res.status_code == 201
    assert res.json()["marketing_consent"] is True


def test_register_driver(client):
    res = client.post(URL, json=payload(role="driver"))
    assert res.status_code == 201
    assert res.json()["role"] == "driver"


def test_cannot_register_admin(client, db):
    res = client.post(URL, json=payload(role="admin"))
    assert res.status_code == 422
    assert db.scalar(select(User).where(User.role == UserRole.ADMIN)) is None


def test_extra_fields_rejected(client):
    res = client.post(URL, json=payload(is_active=False))
    assert res.status_code == 422


def test_email_is_lowercased_and_unique(client):
    assert client.post(URL, json=payload(email="An.Nguyen@Example.com")).status_code == 201
    res = client.post(
        URL, json=payload(username="khac", email="an.nguyen@example.com", phone="0911111111")
    )
    assert res.status_code == 409
    assert res.json()["detail"] == "Email da duoc su dung"


def test_username_is_lowercased_and_unique(client):
    assert client.post(URL, json=payload(username="An.Nguyen")).status_code == 201
    res = client.post(
        URL, json=payload(username="an.nguyen", email="b@example.com", phone="0911111111")
    )
    assert res.status_code == 409
    assert res.json()["detail"] == "Ten dang nhap da duoc su dung"


def test_phone_unique(client):
    assert client.post(URL, json=payload()).status_code == 201
    res = client.post(URL, json=payload(username="khac", email="b@example.com", phone="090 123 4567"))
    assert res.status_code == 409
    assert res.json()["detail"] == "So dien thoai da duoc su dung"


def test_password_12_chars_ok_without_digit(client):
    # AC chi yeu cau toi thieu 12 ky tu, khong bat buoc co so
    res = client.post(URL, json=payload(password="chicochuthoi"))
    assert res.status_code == 201


@pytest.mark.parametrize(
    "field,value",
    [
        ("email", "not-an-email"),
        ("password", "matkhau1234"),     # 11 ky tu
        ("password", "a" * 73),          # > 72 byte
        ("full_name", ""),
        ("full_name", "x" * 101),
        ("phone", "abc123"),
        ("phone", "123"),
        ("phone", ""),                   # bat buoc
        ("phone", None),                 # bat buoc
        ("username", "ab"),              # < 3 ky tu
        ("username", "a" * 31),          # > 30 ky tu
        ("username", "co dau cach"),
        ("username", "tên"),             # co dau
        ("username", ""),
    ],
)
def test_validation_errors(client, field, value):
    res = client.post(URL, json=payload(**{field: value}))
    assert res.status_code == 422


@pytest.mark.parametrize("missing", ["username", "email", "password", "full_name", "phone"])
def test_missing_required_fields(client, missing):
    data = payload()
    del data[missing]
    res = client.post(URL, json=data)
    assert res.status_code == 422
