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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
