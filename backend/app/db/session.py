import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("app.db.session")

engine = None
try:
    # 1. Try connecting to PostgreSQL database
    temp_engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )
    # Test connectivity
    with temp_engine.connect() as conn:
        pass
    engine = temp_engine
    logger.info("Successfully connected to primary PostgreSQL database.")
except (OperationalError, Exception) as e:
    logger.warning(
        f"Failed to connect to primary PostgreSQL database at {settings.DATABASE_URL}. "
        f"Error: {str(e)}. Self-healing to local SQLite database: sqlite:///qyverion.db"
    )
    # 2. Fallback to local SQLite database in workspace
    engine = create_engine(
        "sqlite:///qyverion.db",
        connect_args={"check_same_thread": False}
    )
    
    # 3. Create all tables dynamically on fallback
    try:
        from app.models.log_entry import LogEntry
        from app.models.alert import Alert
        from app.models.threat_indicator import ThreatIndicator
        from app.models.user import User
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Local SQLite database tables initialized successfully.")
    except Exception as create_err:
        logger.error(f"Failed to initialize SQLite fallback database: {str(create_err)}")

# Set up local session maker bound to active database engine
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
