"""
Payment endpoints.

Handles M-Pesa payment disbursements and payment history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4

from app.core.database import get_db
from app.models.payment import Payment
from app.models.monthly_summary import MonthlySummary
from app.models.farmer import Farmer
from app.models.officer import Officer
from app.schemas.payment import (
    PaymentResponse,
    PaymentDisburseRequest,
    PaymentDisburseResponse,
)
from app.api.deps.auth import get_current_user, require_manager

router = APIRouter()


@router.post("/disburse", response_model=PaymentDisburseResponse)
async def disburse_payments(
    disburse_data: PaymentDisburseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """
    Initiate batch M-Pesa B2C payment disbursement.
    
    **Required permissions:** Manager or Admin
    
    **Safety:**
    - `dry_run=true` (default): Simulates payment without actual payout
    - `sandbox=true` (default): Uses sandbox environment
    - Real payments require `ENABLE_REAL_PAYMENTS=true` in environment
    
    **Example:**
    ```json
    {
        "month": "2025-10",
        "dry_run": true,
        "sandbox": true
    }
    ```
    """
    from datetime import datetime
    from decimal import Decimal
    from app.core.config import settings
    
    # Parse month
    try:
        month_date = datetime.strptime(f"{disburse_data.month}-01", "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month format. Use YYYY-MM"
        )
    
    # Safety checks
    if not disburse_data.dry_run and not disburse_data.sandbox:
        if not settings.ENABLE_REAL_PAYMENTS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Real payments are disabled. Set ENABLE_REAL_PAYMENTS=true in environment."
            )
    
    # Get monthly summaries for the month
    query = db.query(MonthlySummary).filter(MonthlySummary.month == month_date)
    
    if disburse_data.farmer_ids:
        query = query.filter(MonthlySummary.farmer_id.in_(disburse_data.farmer_ids))
    
    # Filter summaries with payment above threshold
    query = query.filter(MonthlySummary.estimated_payment >= settings.MINIMUM_PAYMENT_THRESHOLD)
    
    summaries = query.all()
    
    if not summaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summaries found for month {disburse_data.month} meeting payment threshold"
        )
    
    # Create payment records
    payments = []
    total_amount = Decimal("0.00")
    
    for summary in summaries:
        farmer = db.query(Farmer).filter(Farmer.id == summary.farmer_id).first()
        
        payment = Payment(
            farmer_id=farmer.id,
            monthly_summary_id=summary.id,
            amount=summary.estimated_payment,
            currency=summary.currency,
            phone_number=farmer.payment_phone,
            initiated_by=current_user.id,
            status="pending"
        )
        
        # In dry run mode, don't actually process payments
        if disburse_data.dry_run:
            payment.status = "pending"
            payment.metadata = {"dry_run": True, "sandbox": disburse_data.sandbox}
        else:
            # Queue actual payment processing
            # This would be handled by a background worker
            payment.status = "pending"
            payment.metadata = {"sandbox": disburse_data.sandbox}
            # background_tasks.add_task(process_mpesa_payment, payment.id, db)
        
        db.add(payment)
        payments.append(payment)
        total_amount += summary.estimated_payment
    
    db.commit()
    
    # Refresh to get IDs
    for payment in payments:
        db.refresh(payment)
    
    job_id = uuid4()
    
    return PaymentDisburseResponse(
        job_id=job_id,
        total_payments=len(payments),
        total_amount=total_amount,
        status="processing" if not disburse_data.dry_run else "dry_run_complete",
        dry_run=disburse_data.dry_run,
        sandbox=disburse_data.sandbox,
        payments=[PaymentResponse.model_validate(p) for p in payments]
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """
    Get payment details.
    
    **Required permissions:** Manager or Admin
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    return payment


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    farmer_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """
    List payments with pagination and filters.
    
    **Required permissions:** Manager or Admin
    """
    from typing import Optional
    
    query = db.query(Payment)
    
    if farmer_id:
        query = query.filter(Payment.farmer_id == farmer_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    query = query.order_by(Payment.requested_at.desc())
    payments = query.offset(skip).limit(limit).all()
    
    return payments
