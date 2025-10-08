"""Station management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.station import Station
from app.models.officer import Officer
from app.schemas.station import StationCreate, StationUpdate, StationResponse
from app.api.deps.auth import require_manager

router = APIRouter()


@router.post("/", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(
    station_data: StationCreate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """Create a new station. Required permissions: Manager or Admin"""
    # Check for duplicate code
    existing = db.query(Station).filter(Station.code == station_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Station with code {station_data.code} already exists"
        )
    
    station = Station(**station_data.model_dump())
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


@router.get("/", response_model=List[StationResponse])
async def list_stations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """List all stations. Required permissions: Manager or Admin"""
    stations = db.query(Station).offset(skip).limit(limit).all()
    return stations


@router.get("/{station_id}", response_model=StationResponse)
async def get_station(
    station_id: UUID,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_manager)
):
    """Get station details. Required permissions: Manager or Admin"""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return station
