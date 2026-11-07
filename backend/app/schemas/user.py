import re
import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from app.core.security import BCRYPT_MAX_BYTES
from app.models.user import UserRole

PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")
# Chu khong dau, so, dau gach duoi va dau cham; 3-30 ky tu (sau khi chuyen chu thuong)
USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,30}$")
PASSWORD_MIN_LENGTH = 12


class RegisterIn(BaseModel):
    # Khong cho gui them truong la (vd: is_active, password_hash)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str
    email: EmailStr
    # Khong cat khoang trang mat khau (password manager / dan mat khau)
    password: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(
        min_length=PASSWORD_MIN_LENGTH
    )
    full_name: str = Field(min_length=1, max_length=100)
    phone: str
    # Khong bat buoc, mac dinh khong tick (PECR, UK GDPR)
    marketing_consent: bool = False
    # Chi cho phep 2 vai tro nay khi dang ky; admin bi tu choi (422)
    role: Literal["customer", "driver"] = "customer"

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        v = v.lower()
        if not USERNAME_RE.fullmatch(v):
            raise ValueError(
                "Ten dang nhap 3-30 ky tu, chi gom chu khong dau, so, dau _ va dau ."
            )
        return v

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"Mat khau toi da {BCRYPT_MAX_BYTES} byte")
        return v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        v = re.sub(r"[\s\-().]", "", v)
        if not PHONE_RE.fullmatch(v):
            raise ValueError("So dien thoai khong hop le (8-15 chu so, co the bat dau bang +)")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole
    is_active: bool
    marketing_consent: bool
    created_at: datetime
