"""Company model."""

from sqlalchemy import Boolean, Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Company(Base):
    """
    Dairy processor/company model.
    
    Represents dairy processing companies (e.g., Brookside, KCC)
    that operate collection stations.
    """
    
    __tablename__ = "companies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Company information
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(Text)
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stations = relationship("Station", back_populates="company")
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, code={self.code}, name={self.name})>"
