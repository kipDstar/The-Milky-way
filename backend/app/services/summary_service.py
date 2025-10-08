"""
Monthly Summary Service.

Generates aggregated monthly summaries for farmers and calculates estimated payments.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import Optional
import logging

from app.models.monthly_summary import MonthlySummary
from app.models.delivery import Delivery, QualityGrade
from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_monthly_summary(db: Session, farmer_id: UUID, month: date) -> Optional[MonthlySummary]:
    """
    Generate monthly summary for a farmer.
    
    Args:
        db: Database session
        farmer_id: Farmer UUID
        month: Month (first day of month, e.g., 2025-10-01)
        
    Returns:
        MonthlySummary instance or None if no deliveries
    """
    # Get deliveries for the month
    deliveries = db.query(Delivery).filter(
        Delivery.farmer_id == farmer_id,
        func.date_trunc('month', Delivery.delivery_date) == month
    ).all()
    
    if not deliveries:
        logger.info(f"No deliveries found for farmer {farmer_id} in month {month}")
        return None
    
    # Calculate aggregates
    total_liters = sum(float(d.quantity_liters) for d in deliveries)
    total_deliveries = len(deliveries)
    
    # Calculate average fat content (excluding None values)
    fat_contents = [float(d.fat_content) for d in deliveries if d.fat_content is not None]
    avg_fat_content = sum(fat_contents) / len(fat_contents) if fat_contents else None
    
    # Count by quality grade
    grade_a_count = sum(1 for d in deliveries if d.quality_grade == QualityGrade.A)
    grade_b_count = sum(1 for d in deliveries if d.quality_grade == QualityGrade.B)
    grade_c_count = sum(1 for d in deliveries if d.quality_grade == QualityGrade.C)
    rejected_count = sum(1 for d in deliveries if d.quality_grade == QualityGrade.REJECTED)
    
    # Calculate estimated payment
    estimated_payment = calculate_monthly_payment(deliveries)
    
    # Check if summary already exists
    existing_summary = db.query(MonthlySummary).filter(
        MonthlySummary.farmer_id == farmer_id,
        MonthlySummary.month == month
    ).first()
    
    if existing_summary:
        # Update existing summary
        existing_summary.total_liters = Decimal(str(total_liters))
        existing_summary.total_deliveries = total_deliveries
        existing_summary.avg_fat_content = Decimal(str(avg_fat_content)) if avg_fat_content else None
        existing_summary.grade_a_count = grade_a_count
        existing_summary.grade_b_count = grade_b_count
        existing_summary.grade_c_count = grade_c_count
        existing_summary.rejected_count = rejected_count
        existing_summary.estimated_payment = estimated_payment
        
        db.commit()
        db.refresh(existing_summary)
        return existing_summary
    else:
        # Create new summary
        summary = MonthlySummary(
            farmer_id=farmer_id,
            month=month,
            total_liters=Decimal(str(total_liters)),
            total_deliveries=total_deliveries,
            avg_fat_content=Decimal(str(avg_fat_content)) if avg_fat_content else None,
            grade_a_count=grade_a_count,
            grade_b_count=grade_b_count,
            grade_c_count=grade_c_count,
            rejected_count=rejected_count,
            estimated_payment=estimated_payment,
            currency=settings.DEFAULT_CURRENCY
        )
        
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary


def calculate_monthly_payment(deliveries: list[Delivery]) -> Decimal:
    """
    Calculate total estimated payment for a list of deliveries.
    
    Payment formula:
        payment = quantity_liters * price_per_liter * quality_multiplier
    
    Args:
        deliveries: List of Delivery objects
        
    Returns:
        Total estimated payment in Decimal
    """
    total_payment = Decimal("0.00")
    
    for delivery in deliveries:
        # Get quality multiplier
        multiplier = settings.get_quality_multiplier(delivery.quality_grade.value)
        
        # Calculate payment for this delivery
        delivery_payment = (
            Decimal(str(delivery.quantity_liters)) *
            settings.PRICE_PER_LITER *
            multiplier
        )
        
        total_payment += delivery_payment
    
    return total_payment.quantize(Decimal("0.01"))  # Round to 2 decimal places
