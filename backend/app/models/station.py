"""Station model."""

from sqlalchemy import Boolean, Column, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Station(Base):
    """
    Milk collection station model.
    
    Represents physical locations where farmers deliver milk.
    Each station belongs to a company and has assigned officers.
    """
    
    __tablename__ = "stations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Station information
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False)
    address = Column(Text)
    
    # Geolocation (for mobile app, analytics)
    latitude = Column(Numeric(9, 6))  # e.g., -1.286389 (Nairobi)
    longitude = Column(Numeric(9, 6))  # e.g., 36.817223
    
    # Contact
    contact_phone = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="stations")
    farmers = relationship("Farmer", back_populates="station")
    officers = relationship("Officer", back_populates="station")
    deliveries = relationship("Delivery", back_populates="station")
    
    def __repr__(self) -> str:
        return f"<Station(id={self.id}, code={self.code}, name={self.name})>"
