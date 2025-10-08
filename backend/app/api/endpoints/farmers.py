"""
Farmer management endpoints.

Handles farmer registration, profile management, and delivery history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.models.farmer import Farmer
from app.models.delivery import Delivery
from app.models.officer import Officer
from app.schemas.farmer import (
    FarmerCreate,
    FarmerUpdate,
    FarmerResponse,
    FarmerWithRecentDeliveries,
)
from app.schemas.delivery import DeliveryResponse
from app.api.deps.auth import get_current_user, require_officer

router = APIRouter()


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Register a new farmer.
    
    **Required permissions:** Officer, Manager, or Admin
    
    **Example:**
    ```json
    {
        "farmer_code": "FARM-00123",
        "name": "John Doe",
        "national_id": "12345678",
        "phone": "+254712345678",
        "station_id": "uuid-here",
        "village": "Kipkaren"
    }
    ```
    """
    # Check if farmer_code already exists
    existing_farmer = db.query(Farmer).filter(Farmer.farmer_code == farmer_data.farmer_code).first()
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Farmer with code {farmer_data.farmer_code} already exists"
        )
    
    # Check if phone already exists
    existing_phone = db.query(Farmer).filter(Farmer.phone == farmer_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Phone number {farmer_data.phone} is already registered"
        )
    
    # Create farmer
    farmer = Farmer(**farmer_data.model_dump())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    return farmer


@router.get("/{farmer_code}", response_model=FarmerWithRecentDeliveries)
async def get_farmer(
    farmer_code: str,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Get farmer profile and recent delivery history.
    
    Returns farmer details along with last 30 days of deliveries.
    
    **Required permissions:** Officer, Manager, or Admin
    """
    # Find farmer
    farmer = db.query(Farmer).filter(Farmer.farmer_code == farmer_code).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with code {farmer_code} not found"
        )
    
    # Get recent deliveries (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_deliveries = db.query(Delivery).filter(
        Delivery.farmer_id == farmer.id,
        Delivery.delivery_date >= thirty_days_ago.date()
    ).order_by(Delivery.delivery_date.desc()).limit(30).all()
    
    # Calculate totals
    totals = db.query(
        func.count(Delivery.id).label('count'),
        func.sum(Delivery.quantity_liters).label('total_liters')
    ).filter(
        Delivery.farmer_id == farmer.id,
        Delivery.delivery_date >= thirty_days_ago.date()
    ).first()
    
    # Prepare response
    response_data = FarmerWithRecentDeliveries.model_validate(farmer)
    response_data.recent_deliveries = [DeliveryResponse.model_validate(d) for d in recent_deliveries]
    response_data.total_deliveries_last_30_days = totals.count or 0
    response_data.total_liters_last_30_days = float(totals.total_liters or 0)
    
    return response_data


@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    station_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    List farmers with pagination and filters.
    
    **Query parameters:**
    - `skip`: Number of records to skip (pagination)
    - `limit`: Maximum number of records to return
    - `station_id`: Filter by station
    - `is_active`: Filter by active status
    - `search`: Search by name or farmer_code
    
    **Required permissions:** Officer, Manager, or Admin
    """
    query = db.query(Farmer)
    
    # Apply filters
    if station_id:
        query = query.filter(Farmer.station_id == station_id)
    
    if is_active is not None:
        query = query.filter(Farmer.is_active == is_active)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Farmer.name.ilike(search_pattern)) |
            (Farmer.farmer_code.ilike(search_pattern))
        )
    
    # Pagination
    farmers = query.offset(skip).limit(limit).all()
    
    return farmers


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(
    farmer_id: UUID,
    farmer_data: FarmerUpdate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Update farmer information.
    
    **Required permissions:** Officer, Manager, or Admin
    """
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    
    # Update fields
    update_data = farmer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farmer, field, value)
    
    db.commit()
    db.refresh(farmer)
    
    return farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: UUID,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Deactivate a farmer (soft delete).
    
    **Required permissions:** Officer, Manager, or Admin
    """
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    
    # Soft delete (deactivate)
    farmer.is_active = False
    db.commit()
    
    return None
