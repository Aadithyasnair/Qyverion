from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.threat_indicator import ThreatIndicator
from app.schemas.threat_indicator import ThreatIndicatorCreate, ThreatIndicatorResponse

router = APIRouter()


@router.get("/", response_model=List[ThreatIndicatorResponse], summary="Retrieve threat intelligence indicators")
def read_indicators(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> List[ThreatIndicatorResponse]:
    """
    Returns threat indicators of compromise (IoCs) list from the database.
    """
    indicators = (
        db.query(ThreatIndicator)
        .order_by(ThreatIndicator.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return indicators


@router.post("/", response_model=ThreatIndicatorResponse, status_code=status.HTTP_201_CREATED, summary="Create threat indicator")
def create_indicator(
    payload: ThreatIndicatorCreate, 
    db: Session = Depends(get_db)
) -> ThreatIndicatorResponse:
    """
    Appends a new IoC (IP, hash, domain) to the threat pool database.
    """
    # Deduplication check
    existing = (
        db.query(ThreatIndicator)
        .filter(ThreatIndicator.indicator_value == payload.indicator_value)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Threat indicator {payload.indicator_value} already exists."
        )
            
    new_indicator = ThreatIndicator(
        indicator_value=payload.indicator_value,
        indicator_type=payload.indicator_type,
        description=payload.description,
        threat_actor=payload.threat_actor,
        risk_score=payload.risk_score,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(new_indicator)
    db.commit()
    db.refresh(new_indicator)
    return new_indicator
