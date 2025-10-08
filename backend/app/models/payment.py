"""Payment model."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment transaction status."""
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    FAILED = "failed"


class Payment(Base):
    """
    Payment transaction model.
    
    Records M-Pesa B2C payment disbursements to farmers.
    Tracks status and stores M-Pesa response data for reconciliation.
    """
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="RESTRICT"), nullable=False, index=True)
    monthly_summary_id = Column(UUID(as_uuid=True), ForeignKey("monthly_summaries.id", ondelete="SET NULL"))
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="SET NULL"))
    
    # Payment details
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="KES", nullable=False)
    phone_number = Column(String(20), nullable=False)  # M-Pesa phone number
    
    # M-Pesa transaction data
    mpesa_conversation_id = Column(String(255))  # From M-Pesa API
    mpesa_originator_conversation_id = Column(String(255))
    mpesa_transaction_id = Column(String(255), index=True)  # M-Pesa receipt number
    
    # Status tracking
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    failure_reason = Column(Text)
    
    # Additional M-Pesa response data (for debugging and reconciliation)
    metadata = Column(JSONB)
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True))
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="amount_positive"
        ),
    )
    
    # Relationships
    farmer = relationship("Farmer", back_populates="payments")
    monthly_summary = relationship("MonthlySummary", back_populates="payments")
    sms_logs = relationship("SMSLog", back_populates="payment")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, farmer_id={self.farmer_id}, amount={self.amount}, status={self.status})>"
