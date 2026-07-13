from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LogEntryBase(BaseModel):
    raw_data: str = Field(..., description="Raw syslog line or JSON event payload")
    log_source: str = Field(..., min_length=2, max_length=50, description="Source type, e.g. firewall, syslog")
    severity: str = Field(..., min_length=2, max_length=20, description="Log level: INFO, WARNING, CRITICAL")
    source_ip: Optional[str] = Field(None, description="Source IP address if detected")
    destination_ip: Optional[str] = Field(None, description="Destination IP address if detected")
    event_timestamp: datetime = Field(..., description="Time the log event occurred")


class LogEntryCreate(LogEntryBase):
    pass


class LogEntryResponse(LogEntryBase):
    id: int
    ingested_at: datetime

    model_config = ConfigDict(from_attributes=True)

