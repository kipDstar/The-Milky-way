"""Officer (user) management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import hash_password, validate_password_policy
from app.models.officer import Officer
from app.schemas.officer import OfficerCreate, OfficerUpdate, OfficerResponse
from app.api.deps.auth import require_admin, get_current_user

router = APIRouter()


@router.post("/", response_model=OfficerResponse, status_code=status.HTTP_201_CREATED)
async def create_officer(
    officer_data: OfficerCreate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_admin)
):
    """Create a new officer/user. Required permissions: Admin only"""
    # Check if email already exists
    existing = db.query(Officer).filter(Officer.email == officer_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {officer_data.email} already exists"
        )
    
    # Validate password
    is_valid, error_msg = validate_password_policy(officer_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create officer
    officer_dict = officer_data.model_dump(exclude={'password'})
    officer_dict['password_hash'] = hash_password(officer_data.password)
    
    officer = Officer(**officer_dict)
    db.add(officer)
    db.commit()
    db.refresh(officer)
    return officer


@router.get("/me", response_model=OfficerResponse)
async def get_current_officer(
    current_user: Officer = Depends(get_current_user)
):
    """Get current authenticated officer's profile."""
    return current_user


@router.get("/", response_model=List[OfficerResponse])
async def list_officers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_admin)
):
    """List all officers. Required permissions: Admin only"""
    officers = db.query(Officer).offset(skip).limit(limit).all()
    return officers
