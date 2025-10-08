"""
Delivery management endpoints.

Handles milk delivery recording, SMS confirmations, and sync operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from uuid import UUID

from app.core.database import get_db
from app.models.farmer import Farmer
from app.models.delivery import Delivery
from app.models.officer import Officer
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryResponse,
    DeliveryWithRelations,
)
from app.api.deps.auth import get_current_user, require_officer
from app.services.sms_service import send_delivery_confirmation_sms

router = APIRouter()


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    delivery_data: DeliveryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Record a new milk delivery.
    
    Automatically sends SMS confirmation to farmer upon successful creation.
    
    **Required permissions:** Officer, Manager, or Admin
    
    **Example:**
    ```json
    {
        "farmer_code": "FARM-00123",
        "station_id": "uuid-here",
        "officer_id": "uuid-here",
        "delivery_date": "2025-10-08",
        "quantity_liters": 6.8,
        "fat_content": 3.5,
        "quality_grade": "A",
        "remarks": "Good quality"
    }
    ```
    """
    # Resolve farmer by farmer_code
    farmer = db.query(Farmer).filter(Farmer.farmer_code == delivery_data.farmer_code).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with code {delivery_data.farmer_code} not found"
        )
    
    # Check for duplicate if client_generated_id is provided (offline sync)
    if delivery_data.client_generated_id:
        existing = db.query(Delivery).filter(
            Delivery.client_generated_id == delivery_data.client_generated_id
        ).first()
        if existing:
            # Return existing delivery (idempotent)
            response = DeliveryResponse.model_validate(existing)
            response.sms_sent = True  # Assume SMS already sent
            return response
    
    # Create delivery
    delivery_dict = delivery_data.model_dump(exclude={'farmer_code'})
    delivery_dict['farmer_id'] = farmer.id
    delivery_dict['officer_id'] = delivery_data.officer_id or current_user.id
    
    delivery = Delivery(**delivery_dict)
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    
    # Queue SMS confirmation (async background task)
    sms_sent = False
    try:
        background_tasks.add_task(
            send_delivery_confirmation_sms,
            db=db,
            delivery_id=delivery.id
        )
        sms_sent = True
    except Exception as e:
        # Log error but don't fail the delivery creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to queue SMS for delivery {delivery.id}: {e}")
    
    # Prepare response
    response = DeliveryResponse.model_validate(delivery)
    response.sms_sent = sms_sent
    
    return response


@router.get("/{delivery_id}", response_model=DeliveryWithRelations)
async def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Get delivery details with related information.
    
    **Required permissions:** Officer, Manager, or Admin
    """
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID {delivery_id} not found"
        )
    
    # Build response with related entities
    response = DeliveryWithRelations.model_validate(delivery)
    response.farmer_name = delivery.farmer.name
    response.farmer_code = delivery.farmer.farmer_code
    response.station_name = delivery.station.name
    response.officer_name = delivery.officer.name if delivery.officer else None
    
    return response


@router.get("/", response_model=List[DeliveryResponse])
async def list_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    station_id: Optional[UUID] = None,
    farmer_id: Optional[UUID] = None,
    delivery_date: Optional[date] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    List deliveries with pagination and filters.
    
    **Query parameters:**
    - `skip`: Number of records to skip (pagination)
    - `limit`: Maximum number of records to return
    - `station_id`: Filter by station
    - `farmer_id`: Filter by farmer
    - `delivery_date`: Filter by specific date
    - `date_from`: Filter by start date (inclusive)
    - `date_to`: Filter by end date (inclusive)
    
    **Required permissions:** Officer, Manager, or Admin
    """
    query = db.query(Delivery)
    
    # Apply filters
    if station_id:
        query = query.filter(Delivery.station_id == station_id)
    
    if farmer_id:
        query = query.filter(Delivery.farmer_id == farmer_id)
    
    if delivery_date:
        query = query.filter(Delivery.delivery_date == delivery_date)
    else:
        if date_from:
            query = query.filter(Delivery.delivery_date >= date_from)
        if date_to:
            query = query.filter(Delivery.delivery_date <= date_to)
    
    # Order by date descending
    query = query.order_by(Delivery.delivery_date.desc(), Delivery.recorded_at.desc())
    
    # Pagination
    deliveries = query.offset(skip).limit(limit).all()
    
    return deliveries


@router.put("/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(
    delivery_id: UUID,
    delivery_data: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Update delivery information.
    
    **Required permissions:** Officer, Manager, or Admin
    
    **Note:** Typically deliveries should not be edited after creation,
    but this endpoint allows corrections within a reasonable timeframe.
    """
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID {delivery_id} not found"
        )
    
    # Update fields
    update_data = delivery_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(delivery, field, value)
    
    db.commit()
    db.refresh(delivery)
    
    return delivery


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Delete a delivery.
    
    **Required permissions:** Manager or Admin
    
    **Warning:** This permanently deletes the delivery record.
    Use with caution.
    """
    # Only managers and admins can delete
    if not current_user.is_manager():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can delete deliveries"
        )
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID {delivery_id} not found"
        )
    
    db.delete(delivery)
    db.commit()
    
    return None


@router.post("/sync/batch", status_code=status.HTTP_200_OK)
async def sync_batch_deliveries(
    deliveries: List[DeliveryCreate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Batch sync deliveries from offline mobile app.
    
    Accepts multiple deliveries and returns per-record status.
    Handles duplicate detection using client_generated_id.
    
    **Required permissions:** Officer, Manager, or Admin
    """
    results = []
    
    for delivery_data in deliveries:
        try:
            # Resolve farmer
            farmer = db.query(Farmer).filter(Farmer.farmer_code == delivery_data.farmer_code).first()
            if not farmer:
                results.append({
                    "client_id": str(delivery_data.client_generated_id) if delivery_data.client_generated_id else None,
                    "status": "error",
                    "message": f"Farmer {delivery_data.farmer_code} not found"
                })
                continue
            
            # Check for duplicate
            if delivery_data.client_generated_id:
                existing = db.query(Delivery).filter(
                    Delivery.client_generated_id == delivery_data.client_generated_id
                ).first()
                if existing:
                    results.append({
                        "client_id": str(delivery_data.client_generated_id),
                        "delivery_id": str(existing.id),
                        "status": "duplicate",
                        "message": "Delivery already exists"
                    })
                    continue
            
            # Create delivery
            delivery_dict = delivery_data.model_dump(exclude={'farmer_code'})
            delivery_dict['farmer_id'] = farmer.id
            delivery_dict['officer_id'] = delivery_data.officer_id or current_user.id
            
            delivery = Delivery(**delivery_dict)
            db.add(delivery)
            db.flush()  # Get ID without committing
            
            # Queue SMS
            background_tasks.add_task(
                send_delivery_confirmation_sms,
                db=db,
                delivery_id=delivery.id
            )
            
            results.append({
                "client_id": str(delivery_data.client_generated_id) if delivery_data.client_generated_id else None,
                "delivery_id": str(delivery.id),
                "status": "created",
                "message": "Delivery created successfully"
            })
        
        except Exception as e:
            results.append({
                "client_id": str(delivery_data.client_generated_id) if delivery_data.client_generated_id else None,
                "status": "error",
                "message": str(e)
            })
    
    # Commit all successful creations
    db.commit()
    
    return {
        "total": len(deliveries),
        "successful": len([r for r in results if r["status"] == "created"]),
        "duplicates": len([r for r in results if r["status"] == "duplicate"]),
        "errors": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
