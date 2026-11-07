from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.schemas.user import UserOut

# Mat khau giu nguyen tung ky tu (ke ca khoang trang dau/cuoi) de password manager
# va dan mat khau hoat dong dung
RawPassword = Annotated[str, StringConstraints(strip_whitespace=False)]


class LoginIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Email hoac username: co "@" la email, khong co la username
    login: str
    password: RawPassword

    @field_validator("login")
    @classmethod
    def lower_login(cls, v: str) -> str:
        # Email va username deu duoc luu chu thuong khi dang ky
        return v.lower()


class LoginOut(BaseModel):
    # Boc trong "user" de sau nay them thong tin khac ben canh ma frontend khong phai sua
    user: UserOut
