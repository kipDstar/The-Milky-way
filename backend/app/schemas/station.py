"""Station schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class StationBase(BaseModel):
    """Base station schema."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = None
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=6)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=6)
    contact_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')


class StationCreate(StationBase):
    """Schema for creating a station."""
    company_id: UUID


class StationUpdate(BaseModel):
    """Schema for updating a station."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=6)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=6)
    contact_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    is_active: Optional[bool] = None


class StationResponse(StationBase):
    """Schema for station response."""
    id: UUID
    company_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
