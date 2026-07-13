from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("analyst", description="Role: admin, analyst, or viewer")
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plaintext raw user password")


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

