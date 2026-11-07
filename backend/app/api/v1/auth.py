from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import RegisterIn, UserOut
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Email hoac so dien thoai da duoc su dung"}},
)
def register(data: RegisterIn, db: Annotated[Session, Depends(get_db)]) -> UserOut:
    try:
        user = user_service.register_user(db, data)
    except user_service.EmailAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email da duoc su dung")
    except user_service.PhoneAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "So dien thoai da duoc su dung")
    return UserOut.model_validate(user)
