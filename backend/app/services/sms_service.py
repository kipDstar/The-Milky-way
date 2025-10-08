"""
SMS Service.

High-level SMS sending with template support, logging, and retry logic.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from uuid import UUID
import logging

from app.models.sms_log import SMSLog, SMSDirection, SMSStatus
from app.models.delivery import Delivery
from app.models.farmer import Farmer
from app.models.payment import Payment
from app.services.sms_provider import SMSProvider
from app.services.africastalking_provider import AfricasTalkingSMSProvider
from app.services.mock_sms_provider import MockSMSProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_sms_provider() -> SMSProvider:
    """
    Get configured SMS provider instance.
    
    Returns:
        SMSProvider instance based on configuration
    """
    if settings.USE_MOCK_SMS or settings.SMS_PROVIDER == 'mock':
        return MockSMSProvider()
    elif settings.SMS_PROVIDER == 'africastalking':
        return AfricasTalkingSMSProvider()
    elif settings.SMS_PROVIDER == 'twilio':
        # TODO: Implement Twilio provider
        raise NotImplementedError("Twilio provider not yet implemented")
    else:
        logger.warning(f"Unknown SMS provider: {settings.SMS_PROVIDER}, using mock")
        return MockSMSProvider()


# SMS Templates
def get_delivery_confirmation_template(farmer_name: str, quantity: float, date: str, station_name: str, language: str = 'en') -> str:
    """
    Get delivery confirmation SMS template.
    
    Args:
        farmer_name: Farmer's name
        quantity: Liters delivered
        date: Delivery date
        station_name: Station name
        language: Language code ('en' or 'sw')
        
    Returns:
        Formatted SMS message
    """
    if language == 'sw':
        # Swahili template
        return f"Dairy Update: {farmer_name}, umetoa maziwa lita {quantity} tarehe {date} kwa {station_name}. Asante."
    else:
        # English template
        return f"Dairy Update: Dear {farmer_name}, you delivered {quantity} liters of milk on {date} to {station_name}. Thank you."


def get_monthly_summary_template(farmer_name: str, month: str, total_liters: float, amount: float, currency: str, language: str = 'en') -> str:
    """
    Get monthly summary SMS template.
    
    Args:
        farmer_name: Farmer's name
        month: Month (e.g., 'October 2025')
        total_liters: Total liters delivered
        amount: Estimated payment amount
        currency: Currency code
        language: Language code
        
    Returns:
        Formatted SMS message
    """
    if language == 'sw':
        return f"Muhtasari wa Mwezi: {farmer_name}, katika {month} ulitoa lita {total_liters}. Malipo yaliyokadiriwa: {currency} {amount}."
    else:
        return f"Monthly Summary: Dear {farmer_name}, in {month} you delivered {total_liters} liters. Estimated payment: {currency} {amount}."


def get_rejection_template(farmer_name: str, date: str, reason: str, contact: str, language: str = 'en') -> str:
    """Get delivery rejection SMS template."""
    if language == 'sw':
        return f"{farmer_name}, maziwa yako ya tarehe {date} yamekataliwa. Sababu: {reason}. Wasiliana na {contact}."
    else:
        return f"Dear {farmer_name}, your delivery on {date} was rejected. Reason: {reason}. Contact {contact}."


async def send_delivery_confirmation_sms(db: Session, delivery_id: UUID) -> bool:
    """
    Send delivery confirmation SMS to farmer.
    
    Args:
        db: Database session
        delivery_id: Delivery UUID
        
    Returns:
        True if SMS sent successfully, False otherwise
    """
    try:
        # Get delivery with farmer and station
        delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            logger.error(f"Delivery {delivery_id} not found")
            return False
        
        farmer = delivery.farmer
        station = delivery.station
        
        # Check if farmer has phone
        if not farmer.phone:
            logger.warning(f"Farmer {farmer.farmer_code} has no phone number, skipping SMS")
            # Log as failed
            sms_log = SMSLog(
                farmer_id=farmer.id,
                delivery_id=delivery.id,
                phone="",
                message="No phone number available",
                direction=SMSDirection.OUTBOUND,
                status=SMSStatus.FAILED,
                provider="none",
                failure_reason="Farmer has no phone number"
            )
            db.add(sms_log)
            db.commit()
            return False
        
        # Format message
        language = settings.DEFAULT_LANGUAGE
        message = get_delivery_confirmation_template(
            farmer_name=farmer.name,
            quantity=float(delivery.quantity_liters),
            date=delivery.delivery_date.strftime('%Y-%m-%d'),
            station_name=station.name,
            language=language
        )
        
        # Send SMS
        provider = get_sms_provider()
        result = await provider.send_sms(
            phone=farmer.phone,
            message=message,
            metadata={'delivery_id': str(delivery_id)}
        )
        
        # Log SMS
        sms_log = SMSLog(
            farmer_id=farmer.id,
            delivery_id=delivery.id,
            phone=farmer.phone,
            message=message,
            direction=SMSDirection.OUTBOUND,
            status=SMSStatus.SENT if result.success else SMSStatus.FAILED,
            provider=result.metadata.get('provider', 'unknown') if result.metadata else 'unknown',
            provider_message_id=result.provider_message_id,
            provider_status_code=result.status,
            provider_response=result.metadata,
            cost=result.cost,
            sent_at=datetime.utcnow() if result.success else None,
            failed_at=None if result.success else datetime.utcnow()
        )
        db.add(sms_log)
        db.commit()
        
        return result.success
    
    except Exception as e:
        logger.error(f"Failed to send delivery confirmation SMS: {e}", exc_info=True)
        return False


async def send_monthly_summary_sms(db: Session, farmer_id: UUID, month: str, total_liters: float, amount: float) -> bool:
    """
    Send monthly summary SMS to farmer.
    
    Args:
        db: Database session
        farmer_id: Farmer UUID
        month: Month string (e.g., "October 2025")
        total_liters: Total liters delivered
        amount: Estimated payment amount
        
    Returns:
        True if SMS sent successfully
    """
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer or not farmer.phone:
            return False
        
        language = settings.DEFAULT_LANGUAGE
        message = get_monthly_summary_template(
            farmer_name=farmer.name,
            month=month,
            total_liters=total_liters,
            amount=amount,
            currency=settings.DEFAULT_CURRENCY,
            language=language
        )
        
        provider = get_sms_provider()
        result = await provider.send_sms(phone=farmer.phone, message=message)
        
        # Log SMS
        sms_log = SMSLog(
            farmer_id=farmer.id,
            phone=farmer.phone,
            message=message,
            direction=SMSDirection.OUTBOUND,
            status=SMSStatus.SENT if result.success else SMSStatus.FAILED,
            provider=result.metadata.get('provider', 'unknown') if result.metadata else 'unknown',
            provider_message_id=result.provider_message_id,
            sent_at=datetime.utcnow() if result.success else None
        )
        db.add(sms_log)
        db.commit()
        
        return result.success
    
    except Exception as e:
        logger.error(f"Failed to send monthly summary SMS: {e}", exc_info=True)
        return False
