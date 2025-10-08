"""SMS log model."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class SMSDirection(str, enum.Enum):
    """SMS direction."""
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class SMSStatus(str, enum.Enum):
    """SMS delivery status."""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED = "rejected"


class SMSLog(Base):
    """
    SMS communication log model.
    
    Audit trail for all SMS messages (delivery confirmations, monthly summaries, etc.).
    Tracks status and enables retry logic for failed messages.
    """
    
    __tablename__ = "sms_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys (optional - SMS can be sent for various reasons)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="SET NULL"), index=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id", ondelete="SET NULL"), index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), index=True)
    
    # SMS content
    phone = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    direction = Column(Enum(SMSDirection), default=SMSDirection.OUTBOUND, nullable=False)
    
    # Delivery tracking
    status = Column(Enum(SMSStatus), default=SMSStatus.QUEUED, nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # 'africastalking', 'twilio', etc.
    provider_message_id = Column(String(255))  # Provider's message ID
    provider_status_code = Column(String(50))
    provider_response = Column(JSONB)  # Full provider response
    
    # Cost tracking
    cost = Column(Numeric(8, 4))  # Cost in currency units
    
    # Retry management
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    # Relationships
    farmer = relationship("Farmer", back_populates="sms_logs")
    delivery = relationship("Delivery", back_populates="sms_logs")
    payment = relationship("Payment", back_populates="sms_logs")
    
    def __repr__(self) -> str:
        return f"<SMSLog(id={self.id}, phone={self.phone}, status={self.status}, provider={self.provider})>"
