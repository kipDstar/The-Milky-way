"""Payment schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    """Schema for creating a single payment."""
    farmer_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="KES", max_length=3)
    phone_number: str = Field(..., pattern=r'^\+[0-9]{10,15}$')
    monthly_summary_id: Optional[UUID] = None


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: UUID
    farmer_id: UUID
    monthly_summary_id: Optional[UUID]
    amount: Decimal
    currency: str
    phone_number: str
    mpesa_conversation_id: Optional[str]
    mpesa_transaction_id: Optional[str]
    status: PaymentStatus
    failure_reason: Optional[str]
    requested_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentDisburseRequest(BaseModel):
    """Schema for batch payment disbursement."""
    farmer_ids: Optional[List[UUID]] = Field(None, description="Specific farmers (or all if not provided)")
    month: str = Field(..., pattern=r'^\d{4}-\d{2}$', description="Month in YYYY-MM format")
    dry_run: bool = Field(default=True, description="Simulate without actual payout")
    sandbox: bool = Field(default=True, description="Use sandbox environment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": "2025-10",
                "dry_run": True,
                "sandbox": True
            }
        }


class PaymentDisburseResponse(BaseModel):
    """Response for payment disbursement."""
    job_id: UUID
    total_payments: int
    total_amount: Decimal
    status: str
    dry_run: bool
    sandbox: bool
    payments: List[PaymentResponse]
