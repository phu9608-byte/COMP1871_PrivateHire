from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/.env, khong phu thuoc thu muc dang dung khi chay lenh
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    APP_NAME: str = "PrivateHire API"
    API_V1_PREFIX: str = "/api/v1"

    # Bat buoc phai co trong .env (khong de mat khau trong code)
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    # Khoa tai khoan: sai LOGIN_MAX_FAILURES lan trong LOGIN_LOCK_MINUTES phut -> khoa LOGIN_LOCK_MINUTES phut
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    # Phien dang nhap: het sau SESSION_IDLE_MINUTES phut khong hoat dong
    SESSION_IDLE_MINUTES: int = 30
    # Cookie chi gui qua https (localhost / 127.0.0.1 duoc trinh duyet coi la an toan)
    SESSION_COOKIE_SECURE: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
