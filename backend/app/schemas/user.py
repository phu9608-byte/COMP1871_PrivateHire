import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES
from app.models.user import UserRole

PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")


class RegisterIn(BaseModel):
    # Khong cho gui them truong la (vd: is_active, password_hash)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    # Chi cho phep 2 vai tro nay khi dang ky; admin bi tu choi (422)
    role: Literal["customer", "driver"] = "customer"

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"Mat khau toi da {BCRYPT_MAX_BYTES} byte")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"[0-9]", v):
            raise ValueError("Mat khau phai co it nhat 1 chu cai va 1 chu so")
        return v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = re.sub(r"[\s\-().]", "", v)
        if v == "":
            return None
        if not PHONE_RE.fullmatch(v):
            raise ValueError("So dien thoai khong hop le (8-15 chu so, co the bat dau bang +)")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
