import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Uuid, false, func, text, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    ADMIN = "admin"  # chi tao truc tiep trong database, khong dang ky qua API


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # Ten dang nhap, luu chu thuong
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    # Dong y nhan email/tin nhan quang cao (PECR, UK GDPR) - mac dinh khong
    marketing_consent: Mapped[bool] = mapped_column(default=False, server_default=false())
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda e: [m.value for m in e]),
        default=UserRole.CUSTOMER,
        server_default=UserRole.CUSTOMER.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    # Dem so lan dang nhap sai de khoa tai khoan (OWASP A07)
    failed_login_count: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    failed_login_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
