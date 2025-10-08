"""
Safaricom Daraja M-Pesa Payment Provider.

Official docs: https://developer.safaricom.co.ke/Documentation
API Reference: https://developer.safaricom.co.ke/APIs/MobileMoney

SETUP:
1. Register at https://developer.safaricom.co.ke/
2. Create a sandbox app (or production app after approval)
3. Get Consumer Key and Consumer Secret
4. Configure callback URLs for result and timeout
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
import httpx
import base64
import logging

from app.services.payment_provider import PaymentProvider, PaymentResult, PaymentStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class MPesaProvider(PaymentProvider):
    """
    M-Pesa Daraja API implementation.
    
    Environment variables:
    - MPESA_ENVIRONMENT (sandbox or production)
    - MPESA_CONSUMER_KEY
    - MPESA_CONSUMER_SECRET
    - MPESA_SHORTCODE
    - MPESA_INITIATOR_NAME
    - MPESA_INITIATOR_PASSWORD
    - MPESA_B2C_QUEUE_TIMEOUT_URL
    - MPESA_B2C_RESULT_URL
    """
    
    def __init__(self):
        """Initialize M-Pesa provider."""
        self.environment = settings.MPESA_ENVIRONMENT
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.initiator_name = settings.MPESA_INITIATOR_NAME
        self.initiator_password = settings.MPESA_INITIATOR_PASSWORD
        self.queue_timeout_url = settings.MPESA_B2C_QUEUE_TIMEOUT_URL
        self.result_url = settings.MPESA_B2C_RESULT_URL
        
        # Base URLs
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
        
        self.access_token_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        self.b2c_url = f'{self.base_url}/mpesa/b2c/v1/paymentrequest'
        
        logger.info(f"M-Pesa provider initialized (env: {self.environment})")
    
    async def get_access_token(self) -> Optional[str]:
        """
        Get OAuth access token from M-Pesa API.
        
        Returns:
            Access token or None if failed
        """
        try:
            # Create Basic Auth credentials
            credentials = f'{self.consumer_key}:{self.consumer_secret}'
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.access_token_url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                access_token = data.get('access_token')
                
                logger.debug("M-Pesa access token obtained")
                return access_token
        
        except Exception as e:
            logger.error(f"Failed to get M-Pesa access token: {e}", exc_info=True)
            return None
    
    async def disburse_b2c(
        self,
        phone: str,
        amount: Decimal,
        reference: str,
        metadata: Optional[dict] = None
    ) -> PaymentResult:
        """
        Disburse payment via M-Pesa B2C.
        
        Args:
            phone: Phone number (254XXXXXXXXX format)
            amount: Amount to send (KES)
            reference: Payment reference
            metadata: Optional metadata
            
        Returns:
            PaymentResult with transaction details
        """
        try:
            # Safety check
            if not settings.ENABLE_REAL_PAYMENTS:
                logger.warning("Real payments disabled. Returning mock success.")
                return PaymentResult(
                    success=True,
                    conversation_id=f"MOCK-{datetime.utcnow().timestamp()}",
                    transaction_id=f"MOCK-TXN-{datetime.utcnow().timestamp()}",
                    status='mock_success',
                    metadata={
                        'provider': 'mpesa',
                        'environment': 'mock',
                        'note': 'Real payments disabled (ENABLE_REAL_PAYMENTS=false)'
                    }
                )
            
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                return PaymentResult(
                    success=False,
                    status='auth_failed',
                    error_message='Failed to obtain access token'
                )
            
            # Prepare B2C request
            # Note: Security credential is Base64-encoded initiator password (encrypted with M-Pesa public key in production)
            # For sandbox, plain password works
            security_credential = base64.b64encode(self.initiator_password.encode()).decode()
            
            # Normalize phone number (remove + if present)
            phone_normalized = phone.replace('+', '')
            
            payload = {
                'InitiatorName': self.initiator_name,
                'SecurityCredential': security_credential,
                'CommandID': settings.MPESA_COMMAND_ID,  # BusinessPayment, SalaryPayment, or PromotionPayment
                'Amount': int(amount),  # M-Pesa requires integer
                'PartyA': self.shortcode,  # Your shortcode
                'PartyB': phone_normalized,  # Recipient phone
                'Remarks': reference[:100],  # Max 100 chars
                'QueueTimeOutURL': self.queue_timeout_url,
                'ResultURL': self.result_url,
                'Occasion': reference[:100]  # Max 100 chars
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.b2c_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                data = response.json()
                
                # Check response
                # Success response: {'ConversationID': '...', 'OriginatorConversationID': '...', 'ResponseCode': '0', ...}
                # Error response: {'requestId': '...', 'errorCode': '...', 'errorMessage': '...'}
                
                if response.status_code == 200 and data.get('ResponseCode') == '0':
                    return PaymentResult(
                        success=True,
                        conversation_id=data.get('ConversationID'),
                        status='pending',
                        metadata={
                            'provider': 'mpesa',
                            'environment': self.environment,
                            'originator_conversation_id': data.get('OriginatorConversationID'),
                            'response': data
                        }
                    )
                else:
                    error_message = data.get('errorMessage') or data.get('ResponseDescription', 'Unknown error')
                    return PaymentResult(
                        success=False,
                        status='failed',
                        error_message=error_message,
                        metadata={
                            'provider': 'mpesa',
                            'response': data
                        }
                    )
        
        except Exception as e:
            logger.error(f"M-Pesa B2C payment failed: {e}", exc_info=True)
            return PaymentResult(
                success=False,
                status='exception',
                error_message=str(e),
                metadata={'provider': 'mpesa'}
            )
    
    async def check_status(self, conversation_id: str) -> PaymentStatus:
        """
        Check payment status.
        
        Note: M-Pesa uses async callbacks for status updates.
        This method would query the transaction status API if needed.
        
        Args:
            conversation_id: Conversation ID from B2C response
            
        Returns:
            PaymentStatus
        """
        # M-Pesa primarily uses callbacks for status updates
        # For now, return unknown status
        logger.warning("M-Pesa status check not fully implemented (use result callbacks)")
        
        return PaymentStatus(
            status='unknown',
            metadata={
                'note': 'Use result callbacks for status updates',
                'conversation_id': conversation_id
            }
        )
