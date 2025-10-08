"""Company schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = None
    contact_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    contact_email: Optional[str] = Field(None, pattern=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    contact_phone: Optional[str] = Field(None, pattern=r'^\+[0-9]{10,15}$')
    contact_email: Optional[str] = Field(None, pattern=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
