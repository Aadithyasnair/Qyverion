from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
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


class BlockedIPResponse(BaseModel):
    id: int
    ip_address: str
    alert_id: Optional[int]
    rule_name: Optional[str]
    blocked_at: datetime
    status: str

    class Config:
        from_attributes = True


class FeedSyncResponse(BaseModel):
    success: bool
    added_count: int
    message: str





@router.post("/sync", response_model=FeedSyncResponse, summary="Sync threat feeds")
def sync_threat_feeds(db: Session = Depends(get_db)) -> FeedSyncResponse:
    """
    Simulates fetching threat intelligence indicators from AlienVault OTX and AbuseIPDB,
    registering new IoCs in the threat indicator catalog.
    """
    mock_feeds = [
        {"val": "198.51.100.99", "type": "IP", "desc": "Active Brute Force Source (AbuseIPDB Feed)", "actor": "APT41", "score": 90},
        {"val": "203.0.113.88", "type": "IP", "desc": "C2 Server beacon target (AlienVault OTX Feed)", "actor": "CozyBear", "score": 95},
        {"val": "185.220.101.5", "type": "IP", "desc": "Tor Exit Node scanner (Tor Project Feed)", "actor": "MassScanner", "score": 60},
        {"val": "91.240.118.4", "type": "IP", "desc": "Known exploit distribution node", "actor": "FIN7", "score": 85}
    ]

    added = 0
    for feed in mock_feeds:
        existing = db.query(ThreatIndicator).filter(ThreatIndicator.indicator_value == feed["val"]).first()
        if not existing:
            indicator = ThreatIndicator(
                indicator_value=feed["val"],
                indicator_type=feed["type"],
                description=feed["desc"],
                threat_actor=feed["actor"],
                risk_score=feed["score"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(indicator)
            added += 1

    if added > 0:
        db.commit()

    return FeedSyncResponse(
        success=True,
        added_count=added,
        message=f"Threat intelligence feeds synced successfully. Registered {added} new IoCs."
    )


@router.get("/blocked", response_model=List[BlockedIPResponse], summary="Retrieve active firewall blocks")
def get_blocked_ips(db: Session = Depends(get_db)) -> List[BlockedIPResponse]:
    """
    Returns list of all attacker IPs blocked by active SOAR playbooks.
    """
    from app.models.blocked_ip import BlockedIP
    blocks = db.query(BlockedIP).order_by(BlockedIP.blocked_at.desc()).all()
    return blocks
