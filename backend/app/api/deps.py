from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.services import auth_service

SESSION_COOKIE_NAME = "session_id"


def get_current_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
    """Doc cookie session_id; khong co / sai / het han -> 401."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    active = auth_service.get_active_session(db, session_id) if session_id else None
    if active is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Chua dang nhap hoac phien da het han")
    return active.user


CurrentUser = Annotated[User, Depends(get_current_user)]
