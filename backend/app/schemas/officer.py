"""Officer schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.officer import UserRole


class OfficerBase(BaseModel):
    """Base officer schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    role: UserRole = UserRole.OFFICER


class OfficerCreate(OfficerBase):
    """Schema for creating an officer."""
    password: str = Field(..., min_length=8, description="Password (will be hashed)")
    station_id: Optional[UUID] = Field(None, description="Required for officers, optional for managers/admins")


class OfficerUpdate(BaseModel):
    """Schema for updating an officer."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    role: Optional[UserRole] = None
    station_id: Optional[UUID] = None
    two_factor_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class OfficerResponse(OfficerBase):
    """Schema for officer response."""
    id: UUID
    station_id: Optional[UUID]
    two_factor_enabled: bool
    last_login_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
