from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AlertBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str
    severity: str = Field(..., description="Alert severity: LOW, MEDIUM, HIGH, CRITICAL")
    status: str = Field("NEW", description="Alert lifecycle: NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE")
    assigned_to_id: Optional[int] = Field(None, description="ID of assigned analyst user")


class AlertCreate(AlertBase):
    pass


class AlertUpdateStatus(BaseModel):
    status: str = Field(..., description="Target status: NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE")


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

