from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

if not settings.TEST_DATABASE_URL:
    pytest.exit("Chua dat TEST_DATABASE_URL trong .env", returncode=1)

engine = create_engine(settings.TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Iterator[None]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_tables() -> Iterator[None]:
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))  # xoa ca sessions


@pytest.fixture
def db() -> Iterator[Session]:
    with TestingSession() as session:
        yield session


def _get_test_db() -> Iterator[Session]:
    with TestingSession() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = _get_test_db
    # https: cookie "Secure" chi duoc gui lai qua https
    with TestClient(app, base_url="https://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client2(client) -> Iterator[TestClient]:
    """Trinh duyet thu hai (cookie rieng) - dung chung app voi `client`."""
    with TestClient(app, base_url="https://testserver") as c:
        yield c
