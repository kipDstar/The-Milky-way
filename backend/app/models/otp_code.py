"""OTP code model."""

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class OTPCode(Base):
    """
    One-Time Password (OTP) model.
    
    Stores hashed OTP codes for two-factor authentication.
    Codes expire after a short period (typically 5-10 minutes).
    """
    
    __tablename__ = "otp_codes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    officer_id = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # OTP code (stored as hash for security)
    code_hash = Column(String(255), nullable=False)
    
    # Expiration and usage
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "expires_at > CURRENT_TIMESTAMP",
            name="otp_expires_soon"
        ),
    )
    
    # Relationships
    officer = relationship("Officer", back_populates="otp_codes")
    
    def __repr__(self) -> str:
        return f"<OTPCode(id={self.id}, officer_id={self.officer_id}, expires_at={self.expires_at}, used={self.is_used})>"
