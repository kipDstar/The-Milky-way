"""
Payment Provider Interface.

Defines abstract interface for payment providers (M-Pesa, Airtel Money, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime


@dataclass
class PaymentResult:
    """Result of a payment initiation."""
    success: bool
    conversation_id: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str = "unknown"
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class PaymentStatus:
    """Status of a payment transaction."""
    status: str  # 'pending', 'completed', 'failed'
    transaction_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    
    Implementations must provide methods for B2C disbursements and status checks.
    """
    
    @abstractmethod
    async def disburse_b2c(
        self,
        phone: str,
        amount: Decimal,
        reference: str,
        metadata: Optional[dict] = None
    ) -> PaymentResult:
        """
        Disburse funds to a phone number (B2C).
        
        Args:
            phone: Recipient phone number
            amount: Amount to disburse
            reference: Payment reference/description
            metadata: Optional metadata
            
        Returns:
            PaymentResult with transaction details
        """
        pass
    
    @abstractmethod
    async def check_status(self, conversation_id: str) -> PaymentStatus:
        """
        Check the status of a payment transaction.
        
        Args:
            conversation_id: Provider's conversation/transaction identifier
            
        Returns:
            PaymentStatus with current status
        """
        pass
