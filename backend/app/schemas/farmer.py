"""Farmer schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class FarmerBase(BaseModel):
    """Base farmer schema with common fields."""
    farmer_code: str = Field(..., min_length=3, max_length=32, description="Unique farmer code")
    name: str = Field(..., min_length=1, max_length=255)
    national_id: Optional[str] = Field(None, max_length=50)
    phone: str = Field(..., pattern=r'^\+[0-9]{10,15}$', description="E.164 format: +254712345678")
    mpesa_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    village: Optional[str] = Field(None, max_length=255)
    
    @field_validator('farmer_code')
    @classmethod
    def validate_farmer_code(cls, v: str) -> str:
        """Validate farmer code format."""
        if not re.match(r'^[A-Z0-9\-_]{3,32}$', v):
            raise ValueError('Farmer code must contain only uppercase letters, numbers, hyphens, and underscores')
        return v


class FarmerCreate(FarmerBase):
    """Schema for creating a new farmer."""
    station_id: UUID = Field(..., description="Station UUID")


class FarmerUpdate(BaseModel):
    """Schema for updating a farmer."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    national_id: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    mpesa_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    station_id: Optional[UUID] = None
    village: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class FarmerResponse(FarmerBase):
    """Schema for farmer response."""
    id: UUID
    station_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FarmerWithRecentDeliveries(FarmerResponse):
    """Farmer with recent deliveries (for GET /farmers/{farmer_code})."""
    recent_deliveries: List['DeliveryResponse'] = []
    total_deliveries_last_30_days: int = 0
    total_liters_last_30_days: float = 0
    
    class Config:
        from_attributes = True


# Forward reference resolution
from app.schemas.delivery import DeliveryResponse
FarmerWithRecentDeliveries.model_rebuild()
