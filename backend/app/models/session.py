import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


class UserSession(Base):
    """Mot dong = mot lan dang nhap tren mot trinh duyet."""

    __tablename__ = "sessions"

    # Session ID ngau nhien, chinh la gia tri cookie "session_id"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # Xoa user -> database tu xoa cac phien cua user do
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Lan cuoi phien duoc dung - qua 30 phut khong hoat dong thi het phien
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
