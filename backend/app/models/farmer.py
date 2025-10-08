"""Farmer model."""

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Farmer(Base):
    """
    Dairy farmer model.
    
    Represents individual farmers who deliver milk to collection stations.
    Each farmer has a unique farmer_code and is registered at a primary station.
    """
    
    __tablename__ = "farmers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Farmer identification
    farmer_code = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    national_id = Column(String(50))  # Optional, for KYC
    
    # Contact information (E.164 format: +254712345678)
    phone = Column(String(20), nullable=False, index=True)
    mpesa_phone = Column(String(20))  # May differ from primary phone
    
    # Registration
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False)
    village = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "farmer_code ~ '^[A-Z0-9\\-_]{3,32}$'",
            name="farmer_code_format"
        ),
        CheckConstraint(
            "phone ~ '^\\+[0-9]{10,15}$'",
            name="phone_format"
        ),
    )
    
    # Relationships
    station = relationship("Station", back_populates="farmers")
    deliveries = relationship("Delivery", back_populates="farmer")
    monthly_summaries = relationship("MonthlySummary", back_populates="farmer")
    payments = relationship("Payment", back_populates="farmer")
    sms_logs = relationship("SMSLog", back_populates="farmer")
    feedback = relationship("FarmerFeedback", back_populates="farmer")
    
    def __repr__(self) -> str:
        return f"<Farmer(id={self.id}, code={self.farmer_code}, name={self.name})>"
    
    @property
    def payment_phone(self) -> str:
        """Get the phone number to use for payments (M-Pesa)."""
        return self.mpesa_phone or self.phone
