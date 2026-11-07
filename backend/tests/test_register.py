import pytest
from sqlalchemy import select

from app.core.security import verify_password
from app.models.user import User, UserRole

URL = "/api/v1/auth/register"


def payload(**overrides):
    data = {
        "email": "an.nguyen@example.com",
        "password": "matkhau123",
        "full_name": "Nguyen Van An",
        "phone": "0901234567",
    }
    data.update(overrides)
    return data


def test_register_customer_by_default(client, db):
    res = client.post(URL, json=payload())
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "an.nguyen@example.com"
    assert body["role"] == "customer"
    assert body["is_active"] is True
    assert "password" not in body and "password_hash" not in body

    user = db.scalar(select(User).where(User.email == "an.nguyen@example.com"))
    assert user is not None
    assert user.password_hash != "matkhau123"
    assert verify_password("matkhau123", user.password_hash)


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
    res = client.post(URL, json=payload(email="an.nguyen@example.com", phone="0911111111"))
    assert res.status_code == 409
    assert res.json()["detail"] == "Email da duoc su dung"


def test_phone_unique(client):
    assert client.post(URL, json=payload()).status_code == 201
    res = client.post(URL, json=payload(email="other@example.com", phone="090 123 4567"))
    assert res.status_code == 409
    assert res.json()["detail"] == "So dien thoai da duoc su dung"


def test_phone_optional(client):
    assert client.post(URL, json=payload(phone=None)).status_code == 201
    # Nhieu user khong co SDT van hop le
    assert client.post(URL, json=payload(email="b@example.com", phone="")).status_code == 201


@pytest.mark.parametrize(
    "field,value",
    [
        ("email", "not-an-email"),
        ("password", "short1"),          # < 8 ky tu
        ("password", "onlyletters"),     # khong co so
        ("password", "12345678"),        # khong co chu
        ("password", "a1" * 40),         # > 72 byte
        ("full_name", ""),
        ("full_name", "x" * 101),
        ("phone", "abc123"),
        ("phone", "123"),
    ],
)
def test_validation_errors(client, field, value):
    res = client.post(URL, json=payload(**{field: value}))
    assert res.status_code == 422


def test_missing_required_fields(client):
    res = client.post(URL, json={"email": "x@example.com"})
    assert res.status_code == 422
