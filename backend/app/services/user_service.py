from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import RegisterIn


class EmailAlreadyExists(Exception):
    pass


class PhoneAlreadyExists(Exception):
    pass


class UsernameAlreadyExists(Exception):
    pass


def register_user(db: Session, data: RegisterIn) -> User:
    if db.scalar(select(User.id).where(User.username == data.username)) is not None:
        raise UsernameAlreadyExists
    if db.scalar(select(User.id).where(User.email == data.email)) is not None:
        raise EmailAlreadyExists
    if db.scalar(select(User.id).where(User.phone == data.phone)) is not None:
        raise PhoneAlreadyExists

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        marketing_consent=data.marketing_consent,
        role=UserRole(data.role),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        # Hai request dang ky cung luc vuot qua buoc kiem tra o tren
        db.rollback()
        if "username" in str(exc.orig):
            raise UsernameAlreadyExists from exc
        if "phone" in str(exc.orig):
            raise PhoneAlreadyExists from exc
        raise EmailAlreadyExists from exc
    db.refresh(user)
    return user
