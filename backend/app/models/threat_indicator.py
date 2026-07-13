from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ThreatIndicator(Base):
    """
    ThreatIndicator model representing Indicators of Compromise (IoCs)
    used for log matching and incident detection.
    """
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    indicator_value: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    indicator_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # e.g., ip, domain, hash
    description: Mapped[str] = mapped_column(Text, nullable=True)
    threat_actor: Mapped[str] = mapped_column(String(100), index=True, default="Unknown", nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Scale from 0 to 100
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
