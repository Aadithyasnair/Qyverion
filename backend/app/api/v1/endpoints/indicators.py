from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.threat_indicator import ThreatIndicatorCreate, ThreatIndicatorResponse

router = APIRouter()

MOCK_INDICATORS: List[dict] = [
    {
        "id": 1,
        "indicator_value": "203.0.113.5",
        "indicator_type": "ip",
        "description": "Known SSH brute-force attack source",
        "threat_actor": "CozyBear (APT29)",
        "risk_score": 85,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": 2,
        "indicator_value": "malicious-c2-domain.net",
        "indicator_type": "domain",
        "description": "Active C2 beacon destination",
        "threat_actor": "FancyBear (APT28)",
        "risk_score": 95,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
]


@router.get("/", response_model=List[ThreatIndicatorResponse], summary="Retrieve threat intelligence indicators")
def read_indicators(skip: int = 0, limit: int = 100) -> List[ThreatIndicatorResponse]:
    """
    Returns threat indicators of compromise (IoCs) list.
    """
    return MOCK_INDICATORS[skip : skip + limit]


@router.post("/", response_model=ThreatIndicatorResponse, status_code=status.HTTP_201_CREATED, summary="Create threat indicator")
def create_indicator(payload: ThreatIndicatorCreate) -> ThreatIndicatorResponse:
    """
    Appends a new IoC (IP, hash, domain) to the threat pool database.
    """
    # Simple deduplication simulation
    for indicator in MOCK_INDICATORS:
        if indicator["indicator_value"] == payload.indicator_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Threat indicator {payload.indicator_value} already exists."
            )
            
    new_id = len(MOCK_INDICATORS) + 1
    new_indicator = {
        "id": new_id,
        "indicator_value": payload.indicator_value,
        "indicator_type": payload.indicator_type,
        "description": payload.description,
        "threat_actor": payload.threat_actor,
        "risk_score": payload.risk_score,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    MOCK_INDICATORS.append(new_indicator)
    return new_indicator
