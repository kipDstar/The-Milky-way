"""Refresh token model."""

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class RefreshToken(Base):
    """
    Refresh token model.
    
    Stores hashed refresh tokens for JWT authentication flow.
    Enables token revocation and session management.
    """
    
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    officer_id = Column(UUID(as_uuid=True), ForeignKey("officers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token (stored as hash for security)
    token_hash = Column(String(255), unique=True, nullable=False)
    
    # Expiration and revocation
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    
    # Request context (for security analysis)
    ip_address = Column(INET)
    user_agent = Column(String(500))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    officer = relationship("Officer", back_populates="refresh_tokens")
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, officer_id={self.officer_id}, expires_at={self.expires_at}, revoked={self.is_revoked})>"
