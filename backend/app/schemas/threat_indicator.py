from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ThreatIndicatorBase(BaseModel):
    indicator_value: str = Field(..., description="The indicator, e.g., an IP address, domain, or SHA256 hash")
    indicator_type: str = Field(..., description="Type of indicator: ip, domain, or hash")
    description: Optional[str] = Field(None, description="Detailed context about the threat indicator")
    threat_actor: str = Field("Unknown", description="APT group or threat actor name")
    risk_score: int = Field(0, ge=0, le=100, description="Risk ranking from 0 to 100")


class ThreatIndicatorCreate(ThreatIndicatorBase):
    pass


class ThreatIndicatorResponse(ThreatIndicatorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

