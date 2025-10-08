"""Officer (user) model."""

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    OFFICER = "officer"
    MANAGER = "manager"
    ADMIN = "admin"


class Officer(Base):
    """
    System user (officer, manager, or admin) model.
    
    Represents staff members who interact with the system.
    Officers record deliveries, managers view reports, admins manage the system.
    """
    
    __tablename__ = "officers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OFFICER, index=True)
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255))  # TOTP secret (encrypted)
    
    # Station assignment (null for admins/managers who can access all stations)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id", ondelete="RESTRICT"))
    
    # Activity tracking
    last_login_at = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name="email_format"
        ),
    )
    
    # Relationships
    station = relationship("Station", back_populates="officers")
    deliveries = relationship("Delivery", back_populates="officer")
    refresh_tokens = relationship("RefreshToken", back_populates="officer")
    otp_codes = relationship("OTPCode", back_populates="officer")
    
    def __repr__(self) -> str:
        return f"<Officer(id={self.id}, email={self.email}, role={self.role})>"
    
    def has_role(self, *roles: UserRole) -> bool:
        """Check if officer has any of the specified roles."""
        return self.role in roles
    
    def is_admin(self) -> bool:
        """Check if officer is an admin."""
        return self.role == UserRole.ADMIN
    
    def is_manager(self) -> bool:
        """Check if officer is a manager or admin."""
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)
