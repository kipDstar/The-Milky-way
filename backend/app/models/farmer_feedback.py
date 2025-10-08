"""Farmer feedback model."""

from sqlalchemy import Boolean, Column, String, DateTime, Integer, ForeignKey, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class FarmerFeedback(Base):
    """
    Farmer feedback model.
    
    Stores feedback from farmers about service quality, payments, and operations.
    Can be submitted via SMS, web, or mobile app.
    """
    
    __tablename__ = "farmer_feedback"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id", ondelete="SET NULL"))
    
    # Feedback content
    category = Column(String(50))  # 'quality', 'payment', 'service', 'other'
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    source = Column(String(50), default="sms")  # 'sms', 'web', 'mobile', 'call'
    
    # Resolution tracking
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="SET NULL"))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "rating IS NULL OR (rating >= 1 AND rating <= 5)",
            name="rating_range"
        ),
    )
    
    # Relationships
    farmer = relationship("Farmer", back_populates="feedback")
    delivery = relationship("Delivery", back_populates="feedback")
    
    def __repr__(self) -> str:
        return f"<FarmerFeedback(id={self.id}, farmer_id={self.farmer_id}, rating={self.rating}, resolved={self.is_resolved})>"
