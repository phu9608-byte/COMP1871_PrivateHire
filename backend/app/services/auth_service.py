import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserSession


class InvalidCredentials(Exception):
    pass


class InactiveUser(Exception):
    pass


class AccountLocked(Exception):
    pass


def _record_failure(db: Session, user: User, now: datetime) -> None:
    window = timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
    started = user.failed_login_started_at
    if started is None or now - started >= window:
        # Lan sai dau tien trong cua so 15 phut moi
        user.failed_login_count = 1
        user.failed_login_started_at = now
    else:
        user.failed_login_count += 1
    if user.failed_login_count >= settings.LOGIN_MAX_FAILURES:
        user.locked_until = now + window
        user.failed_login_count = 0
        user.failed_login_started_at = None
    db.commit()


def _reset_failures(db: Session, user: User) -> None:
    if user.failed_login_count or user.failed_login_started_at or user.locked_until:
        user.failed_login_count = 0
        user.failed_login_started_at = None
        user.locked_until = None
        db.commit()


def authenticate(db: Session, login: str, password: str) -> User:
    now = datetime.now(UTC)
    # Username khong cho phep "@", nen co "@" chac chan la email
    column = User.email if "@" in login else User.username
    user = db.scalar(select(User).where(column == login))
    # Sai thong tin nao cung bao cung mot loi, khong noi truong nao sai (AC 2)
    if user is None:
        raise InvalidCredentials
    # Dang bi khoa: chan ca khi mat khau dung, khong dem them, khong keo dai khoa (AC 4)
    if user.locked_until is not None and user.locked_until > now:
        raise AccountLocked
    if not verify_password(password, user.password_hash):
        _record_failure(db, user, now)
        raise InvalidCredentials
    _reset_failures(db, user)
    # Chi bao "bi khoa" khi mat khau da dung
    if not user.is_active:
        raise InactiveUser
    return user


# ---------- Phien dang nhap (session) ----------

def create_session(db: Session, user: User, old_session_id: str | None) -> UserSession:
    """Cap session ID moi moi lan dang nhap (AC 5); xoa phien cu cua trinh duyet nay neu co."""
    if old_session_id:
        db.execute(delete(UserSession).where(UserSession.id == old_session_id))
    new_session = UserSession(
        id=secrets.token_urlsafe(32), user_id=user.id, last_seen_at=datetime.now(UTC)
    )
    db.add(new_session)
    db.commit()
    return new_session


def get_active_session(db: Session, session_id: str) -> UserSession | None:
    """Tra phien con hieu luc va gia han them 30 phut; het han thi xoa (AC 5)."""
    found = db.get(UserSession, session_id)
    if found is None:
        return None
    now = datetime.now(UTC)
    if now - found.last_seen_at >= timedelta(minutes=settings.SESSION_IDLE_MINUTES):
        db.delete(found)
        db.commit()
        return None
    if not found.user.is_active:
        return None
    found.last_seen_at = now
    db.commit()
    return found


def end_session(db: Session, session_id: str) -> None:
    """Dang xuat: xoa phien (AC 3)."""
    db.execute(delete(UserSession).where(UserSession.id == session_id))
    db.commit()


def delete_all_sessions(db: Session, user_id: uuid.UUID) -> int:
    """Xoa moi phien cua user - danh cho doi mat khau / admin khoa tai khoan sau nay."""
    result = db.execute(delete(UserSession).where(UserSession.user_id == user_id))
    db.commit()
    return result.rowcount
