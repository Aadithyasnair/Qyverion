from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.log_entry import LogEntry
from app.schemas.log_entry import LogEntryCreate, LogEntryResponse
from app.services.log_ingestion import LogIngestionService

router = APIRouter()


@router.get("/", response_model=List[LogEntryResponse], summary="Retrieve ingested logs")
def read_logs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> List[LogEntryResponse]:
    """
    Returns a list of parsed logs from the database, sorted by ingestion time (descending).
    """
    logs = (
        db.query(LogEntry)
        .order_by(LogEntry.ingested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs


@router.post("/ingest", response_model=LogEntryResponse, status_code=status.HTTP_201_CREATED, summary="Ingest log entry")
def ingest_log(
    payload: LogEntryCreate, 
    db: Session = Depends(get_db)
) -> LogEntryResponse:
    """
    Ingests, parses, matches against threat intel, and saves a new log entry.
    Automatically generates alerts if malicious source/destination IPs are detected.
    """
    try:
        service = LogIngestionService(db)
        db_log = service.ingest(payload)
        return db_log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"In-depth parsing failed: {str(e)}"
        )
