"""
Mock SMS Provider for testing and development.

Logs SMS instead of sending to save costs during development.
"""

from typing import Optional
from datetime import datetime
import logging
import uuid

from app.services.sms_provider import SMSProvider, SMSResult, SMSStatus

logger = logging.getLogger(__name__)


class MockSMSProvider(SMSProvider):
    """
    Mock SMS provider for testing.
    
    Logs SMS messages instead of actually sending them.
    Always returns success.
    """
    
    async def send_sms(self, phone: str, message: str, metadata: Optional[dict] = None) -> SMSResult:
        """
        Mock SMS send (logs only).
        
        Args:
            phone: Recipient phone number
            message: Message text
            metadata: Optional metadata
            
        Returns:
            SMSResult with mock success
        """
        message_id = f"MOCK-{uuid.uuid4().hex[:12]}"
        
        logger.info(f"""
        ============================================
        MOCK SMS SENT
        ============================================
        To: {phone}
        Message: {message}
        Message ID: {message_id}
        Metadata: {metadata}
        ============================================
        """)
        
        return SMSResult(
            success=True,
            provider_message_id=message_id,
            status='sent',
            cost=0.0,
            metadata={
                'provider': 'mock',
                'note': 'This is a mock SMS, not actually sent'
            }
        )
    
    async def check_status(self, provider_message_id: str) -> SMSStatus:
        """
        Mock status check.
        
        Always returns delivered.
        """
        return SMSStatus(
            status='delivered',
            delivered_at=datetime.utcnow(),
            metadata={
                'provider': 'mock',
                'message_id': provider_message_id
            }
        )
