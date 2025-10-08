"""Audit log model."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.officer import UserRole


class AuditLog(Base):
    """
    Audit trail model.
    
    Records all critical operations for compliance and traceability.
    Stores before/after state changes for forensic analysis.
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What was changed
    entity_type = Column(String(100), nullable=False, index=True)  # 'farmer', 'delivery', 'payment', etc.
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'created', 'updated', 'deleted', 'approved', etc.
    
    # Who made the change
    actor_id = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="SET NULL"))
    actor_role = Column(String(50))  # Denormalized for historical accuracy
    
    # Change details (JSON diff of before/after state)
    changes = Column(JSONB)
    
    # Request context
    ip_address = Column(INET)
    user_agent = Column(String(500))
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, entity_type={self.entity_type}, action={self.action}, timestamp={self.timestamp})>"
