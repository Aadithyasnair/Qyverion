from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create PostgreSQL database engine using SQLAlchemy 2.x syntax
# pool_pre_ping=True checks connection status and reconnects if dropped
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL queries logging in debug mode
)

# Set up local session maker bound to database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Automatically closes the session after response completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
