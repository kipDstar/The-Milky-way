"""
Africa's Talking SMS Provider Implementation.

Official docs: https://developers.africastalking.com/docs/sms/overview
"""

from typing import Optional
import africastalking
import logging

from app.services.sms_provider import SMSProvider, SMSResult, SMSStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class AfricasTalkingSMSProvider(SMSProvider):
    """
    Africa's Talking SMS provider implementation.
    
    Configuration via environment variables:
    - AFRICASTALKING_USERNAME
    - AFRICASTALKING_API_KEY
    - AFRICASTALKING_SENDER_ID
    - AFRICASTALKING_ENVIRONMENT (sandbox or production)
    """
    
    def __init__(self):
        """Initialize Africa's Talking SDK."""
        # Initialize SDK
        africastalking.initialize(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY
        )
        
        # Get SMS service
        self.sms = africastalking.SMS
        self.sender_id = settings.AFRICASTALKING_SENDER_ID
        
        logger.info(f"Africa's Talking SMS provider initialized (env: {settings.AFRICASTALKING_ENVIRONMENT})")
    
    async def send_sms(self, phone: str, message: str, metadata: Optional[dict] = None) -> SMSResult:
        """
        Send SMS via Africa's Talking.
        
        Args:
            phone: E.164 format phone number (e.g., +254712345678)
            message: Message text (max 160 chars for single SMS)
            metadata: Optional dict with 'sender_id', 'callback_url', etc.
            
        Returns:
            SMSResult with send status
        """
        try:
            # Extract metadata
            sender_id = metadata.get('sender_id', self.sender_id) if metadata else self.sender_id
            
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=[phone],
                sender_id=sender_id
            )
            
            # Parse response
            # Africa's Talking returns: {'SMSMessageData': {'Message': '...', 'Recipients': [...]}}
            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            
            if recipients and len(recipients) > 0:
                recipient_data = recipients[0]
                status = recipient_data.get('status', 'Unknown')
                message_id = recipient_data.get('messageId')
                cost = recipient_data.get('cost')
                
                # Check if successful
                # Status can be: 'Success', 'InvalidPhoneNumber', 'InsufficientBalance', etc.
                success = status.lower() in ['success', 'sent']
                
                return SMSResult(
                    success=success,
                    provider_message_id=message_id,
                    status=status,
                    cost=float(cost.replace('KES ', '')) if cost else None,
                    metadata={
                        'provider': 'africastalking',
                        'response': recipient_data
                    }
                )
            else:
                return SMSResult(
                    success=False,
                    status='failed',
                    error_message='No recipients in response',
                    metadata={'response': response}
                )
        
        except Exception as e:
            logger.error(f"Africa's Talking SMS send failed: {e}", exc_info=True)
            return SMSResult(
                success=False,
                status='failed',
                error_message=str(e),
                metadata={'provider': 'africastalking'}
            )
    
    async def check_status(self, provider_message_id: str) -> SMSStatus:
        """
        Check SMS delivery status.
        
        Note: Africa's Talking doesn't provide a direct status query API.
        Status updates come via delivery report callbacks.
        
        Args:
            provider_message_id: Message ID from send response
            
        Returns:
            SMSStatus (limited info without callback data)
        """
        # Africa's Talking requires callback URL for delivery reports
        # For now, return unknown status
        logger.warning("Africa's Talking status check not implemented (use delivery report callbacks)")
        
        return SMSStatus(
            status='unknown',
            metadata={
                'note': 'Use delivery report callbacks for status updates',
                'message_id': provider_message_id
            }
        )
