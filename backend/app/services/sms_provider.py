"""
SMS Provider Adapter Interface.

Defines abstract interface for SMS providers to enable easy swapping
between Africa's Talking, Twilio, and other providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class SMSResult:
    """Result of an SMS send operation."""
    success: bool
    provider_message_id: Optional[str] = None
    status: str = "unknown"
    error_message: Optional[str] = None
    cost: Optional[float] = None
    metadata: Optional[dict] = None


@dataclass
class SMSStatus:
    """Status of a sent SMS."""
    status: str  # 'queued', 'sent', 'delivered', 'failed', 'rejected'
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class SMSProvider(ABC):
    """
    Abstract base class for SMS providers.
    
    Implementations must provide methods for sending SMS and checking status.
    """
    
    @abstractmethod
    async def send_sms(self, phone: str, message: str, metadata: Optional[dict] = None) -> SMSResult:
        """
        Send an SMS message.
        
        Args:
            phone: Recipient phone number in E.164 format
            message: Message text
            metadata: Optional metadata (sender_id, priority, etc.)
            
        Returns:
            SMSResult with success status and provider details
        """
        pass
    
    @abstractmethod
    async def check_status(self, provider_message_id: str) -> SMSStatus:
        """
        Check the delivery status of a sent SMS.
        
        Args:
            provider_message_id: Provider's message identifier
            
        Returns:
            SMSStatus with current delivery status
        """
        pass
