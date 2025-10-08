"""Company management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.company import Company
from app.models.officer import Officer
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.api.deps.auth import require_admin

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_admin)
):
    """Create a new company. Required permissions: Admin only"""
    existing = db.query(Company).filter(Company.code == company_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with code {company_data.code} already exists"
        )
    
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_admin)
):
    """List all companies. Required permissions: Admin only"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies
