import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add backend directory to sys.path so tests can find app package
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# In-memory SQLite database setup for unit and integration testing
SQLITE_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Needed for in-memory SQLite to share connections
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Generator[None, None, None]:
    """
    Creates the database schema in SQLite before the test session starts
    and drops it afterward.
    """
    # Create all tables in SQLite
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after testing completes
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Fixture that yields an isolated transactional database session.
    Rolls back any changes committed during testing to keep the state clean.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def override_db_dependency(db: Session) -> Generator[None, None, None]:
    """
    Overrides the FastAPI get_db dependency to use the isolated test session.
    """
    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    TestClient fixture for making HTTP requests to endpoints.
    """
    with TestClient(app) as c:
        yield c
