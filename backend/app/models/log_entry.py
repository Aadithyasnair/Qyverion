from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class LogEntry(Base):
    """
    LogEntry model representing ingested logs from firewalls, servers, and applications.
    """
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_data: Mapped[str] = mapped_column(Text, nullable=False)  # Raw syslog or JSON string
    log_source: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., firewall, windows_ad
    severity: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # e.g., INFO, WARNING, CRITICAL
    source_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=True)  # Supports IPv4 and IPv6
    destination_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
