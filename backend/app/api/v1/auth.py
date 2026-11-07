from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import SESSION_COOKIE_NAME, CurrentUser
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import LoginIn, LoginOut
from app.schemas.user import RegisterIn, UserOut
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Ten dang nhap, email hoac so dien thoai da duoc su dung"}},
)
def register(data: RegisterIn, db: Annotated[Session, Depends(get_db)]) -> UserOut:
    try:
        user = user_service.register_user(db, data)
    except user_service.UsernameAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ten dang nhap da duoc su dung")
    except user_service.EmailAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email da duoc su dung")
    except user_service.PhoneAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "So dien thoai da duoc su dung")
    return UserOut.model_validate(user)


def _no_store(response: Response) -> None:
    # Khong cho trinh duyet luu lai du lieu dang nhap (nut Back - AC 3)
    response.headers["Cache-Control"] = "no-store"


@router.post(
    "/login",
    response_model=LoginOut,
    responses={
        401: {"description": "Thong tin dang nhap khong dung"},
        403: {"description": "Tai khoan da bi khoa"},
        429: {"description": "Dang nhap sai qua nhieu lan, thu lai sau 15 phut"},
    },
)
def login(
    data: LoginIn,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> LoginOut:
    """Dang nhap bang email hoac username. Thanh cong -> cookie `session_id` (HttpOnly, Secure)."""
    _no_store(response)
    try:
        user = auth_service.authenticate(db, data.login, data.password)
    except auth_service.InvalidCredentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Thong tin dang nhap khong dung")
    except auth_service.AccountLocked:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Dang nhap sai qua nhieu lan, thu lai sau 15 phut"
        )
    except auth_service.InactiveUser:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tai khoan da bi khoa")

    new_session = auth_service.create_session(
        db, user, old_session_id=request.cookies.get(SESSION_COOKIE_NAME)
    )
    # Khong dat Max-Age: tat han trinh duyet la mat cookie; 30 phut do server kiem soat
    response.set_cookie(
        SESSION_COOKIE_NAME,
        new_session.id,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return LoginOut(user=UserOut.model_validate(user))


@router.get(
    "/me",
    response_model=UserOut,
    responses={401: {"description": "Chua dang nhap hoac phien da het han"}},
)
def me(user: CurrentUser, response: Response) -> UserOut:
    """Thong tin user dang dang nhap - dashboard goi moi khi mo trang."""
    _no_store(response)
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Dang xuat: xoa phien o server va xoa cookie (AC 3). Chua dang nhap van tra 204."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        auth_service.end_session(db, session_id)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _no_store(response)
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return response
