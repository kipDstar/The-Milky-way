"""Delivery model."""

from sqlalchemy import Boolean, Column, String, DateTime, Date, Numeric, ForeignKey, Enum, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class QualityGrade(str, enum.Enum):
    """Milk quality grades."""
    A = "A"
    B = "B"
    C = "C"
    REJECTED = "Rejected"


class DeliverySource(str, enum.Enum):
    """Source of delivery entry."""
    MOBILE = "mobile"
    WEB = "web"
    BATCH = "batch"


class SyncStatus(str, enum.Enum):
    """Offline sync status."""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"


class Delivery(Base):
    """
    Milk delivery transaction model.
    
    Core entity representing a farmer's milk delivery to a station.
    Records quantity, quality, and metadata for payment calculation.
    """
    
    __tablename__ = "deliveries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="RESTRICT"), nullable=False, index=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False, index=True)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="SET NULL"), index=True)
    
    # Delivery information
    delivery_date = Column(Date, nullable=False, index=True)  # Local date (YYYY-MM-DD)
    quantity_liters = Column(Numeric(8, 3), nullable=False)  # e.g., 6.800
    fat_content = Column(Numeric(5, 2))  # Percentage, e.g., 3.75
    quality_grade = Column(Enum(QualityGrade), nullable=False, default=QualityGrade.B)
    remarks = Column(Text)
    
    # Metadata
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    source = Column(Enum(DeliverySource), default=DeliverySource.MOBILE, nullable=False)
    
    # Offline sync support
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.SYNCED, nullable=False)
    client_generated_id = Column(UUID(as_uuid=True), index=True)  # UUID from mobile app
    
    # Updated timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "quantity_liters > 0",
            name="quantity_positive"
        ),
        CheckConstraint(
            "quantity_liters <= 1000",
            name="quantity_reasonable"
        ),
        CheckConstraint(
            "fat_content IS NULL OR (fat_content >= 0 AND fat_content <= 20)",
            name="fat_content_range"
        ),
    )
    
    # Relationships
    farmer = relationship("Farmer", back_populates="deliveries")
    station = relationship("Station", back_populates="deliveries")
    officer = relationship("Officer", back_populates="deliveries")
    sms_logs = relationship("SMSLog", back_populates="delivery")
    feedback = relationship("FarmerFeedback", back_populates="delivery")
    
    def __repr__(self) -> str:
        return f"<Delivery(id={self.id}, farmer_id={self.farmer_id}, date={self.delivery_date}, liters={self.quantity_liters})>"
    
    def calculate_payment_amount(self, price_per_liter, grade_multiplier) -> float:
        """
        Calculate payment amount for this delivery.
        
        Args:
            price_per_liter: Base price per liter
            grade_multiplier: Quality grade multiplier
            
        Returns:
            Payment amount in currency
        """
        return float(self.quantity_liters) * float(price_per_liter) * float(grade_multiplier)
