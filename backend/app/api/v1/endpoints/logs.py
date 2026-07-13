from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.log_entry import LogEntryCreate, LogEntryResponse

router = APIRouter()

# Mock in-memory database to store logs during runtime for verification
MOCK_LOGS: List[dict] = [
    {
        "id": 1,
        "raw_data": "192.168.1.105 - - [13/Jul/2026:20:10:00 +0000] \"GET /admin HTTP/1.1\" 401 532",
        "log_source": "nginx_access",
        "severity": "WARNING",
        "source_ip": "192.168.1.105",
        "destination_ip": "192.168.1.10",
        "event_timestamp": datetime.now(timezone.utc),
        "ingested_at": datetime.now(timezone.utc),
    },
    {
        "id": 2,
        "raw_data": "pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=203.0.113.5 user=root",
        "log_source": "syslog_auth",
        "severity": "CRITICAL",
        "source_ip": "203.0.113.5",
        "destination_ip": "192.168.1.20",
        "event_timestamp": datetime.now(timezone.utc),
        "ingested_at": datetime.now(timezone.utc),
    }
]


@router.get("/", response_model=List[LogEntryResponse], summary="Retrieve ingested logs")
def read_logs(skip: int = 0, limit: int = 100) -> List[LogEntryResponse]:
    """
    Returns a list of ingested logs (currently simulated).
    """
    return MOCK_LOGS[skip : skip + limit]


@router.post("/ingest", response_model=LogEntryResponse, status_code=status.HTTP_201_CREATED, summary="Ingest log entry")
def ingest_log(payload: LogEntryCreate) -> LogEntryResponse:
    """
    Ingests and parses a new log event.
    """
    new_id = len(MOCK_LOGS) + 1
    new_log = {
        "id": new_id,
        "raw_data": payload.raw_data,
        "log_source": payload.log_source,
        "severity": payload.severity,
        "source_ip": payload.source_ip,
        "destination_ip": payload.destination_ip,
        "event_timestamp": payload.event_timestamp,
        "ingested_at": datetime.now(timezone.utc),
    }
    MOCK_LOGS.append(new_log)
    return new_log
