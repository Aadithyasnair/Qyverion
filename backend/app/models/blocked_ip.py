from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class BlockedIP(Base):
    """
    BlockedIP model representing IP addresses currently blocked by the SOAR system.
    """
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), unique=True, index=True, nullable=False)
    alert_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alert.id", ondelete="SET NULL"), nullable=True)
    rule_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blocked_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True, nullable=False)  # ACTIVE or RELEASED
