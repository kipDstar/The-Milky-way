"""Delivery schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

from app.models.delivery import QualityGrade, DeliverySource, SyncStatus


class DeliveryBase(BaseModel):
    """Base delivery schema."""
    delivery_date: date = Field(..., description="Delivery date (YYYY-MM-DD)")
    quantity_liters: Decimal = Field(..., ge=0.1, le=1000, decimal_places=3, description="Quantity in liters")
    fat_content: Optional[Decimal] = Field(None, ge=0, le=20, decimal_places=2, description="Fat content percentage")
    quality_grade: QualityGrade = Field(default=QualityGrade.B)
    remarks: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    """Schema for creating a delivery."""
    farmer_code: str = Field(..., description="Farmer code (will be resolved to farmer_id)")
    station_id: UUID
    officer_id: Optional[UUID] = None
    source: DeliverySource = DeliverySource.MOBILE
    client_generated_id: Optional[UUID] = Field(None, description="UUID from mobile app for offline sync")


class DeliveryUpdate(BaseModel):
    """Schema for updating a delivery."""
    quantity_liters: Optional[Decimal] = Field(None, ge=0.1, le=1000, decimal_places=3)
    fat_content: Optional[Decimal] = Field(None, ge=0, le=20, decimal_places=2)
    quality_grade: Optional[QualityGrade] = None
    remarks: Optional[str] = None
    sync_status: Optional[SyncStatus] = None


class DeliveryResponse(DeliveryBase):
    """Schema for delivery response."""
    id: UUID
    farmer_id: UUID
    station_id: UUID
    officer_id: Optional[UUID]
    recorded_at: datetime
    source: DeliverySource
    sync_status: SyncStatus
    client_generated_id: Optional[UUID]
    updated_at: datetime
    sms_sent: Optional[bool] = Field(None, description="Indicates if SMS was sent successfully")
    
    class Config:
        from_attributes = True


class DeliveryWithRelations(DeliveryResponse):
    """Delivery with related entities (farmer, station, officer names)."""
    farmer_name: str
    farmer_code: str
    station_name: str
    officer_name: Optional[str] = None
    
    class Config:
        from_attributes = True
