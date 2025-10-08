"""
Reporting endpoints.

Provides daily and monthly aggregated reports for analytics.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.models.delivery import Delivery, QualityGrade
from app.models.farmer import Farmer
from app.models.station import Station
from app.models.monthly_summary import MonthlySummary
from app.models.officer import Officer
from app.schemas.report import (
    DailyReportResponse,
    DailyStationTotal,
    DailyFarmerTotal,
    MonthlyReportResponse,
    MonthlyFarmerSummary,
)
from app.api.deps.auth import get_current_user, require_officer

router = APIRouter()


@router.get("/daily", response_model=DailyReportResponse)
async def get_daily_report(
    report_date: date = Query(..., description="Date for the report"),
    station_id: Optional[UUID] = Query(None, description="Filter by station"),
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Get daily delivery report.
    
    Returns aggregated totals by station and by farmer for a specific date.
    
    **Required permissions:** Officer, Manager, or Admin
    """
    # Station totals query
    station_query = db.query(
        Delivery.station_id,
        Station.name.label('station_name'),
        func.count(Delivery.id).label('delivery_count'),
        func.sum(Delivery.quantity_liters).label('total_liters'),
        func.avg(Delivery.fat_content).label('avg_fat_content'),
        func.count().filter(Delivery.quality_grade == QualityGrade.A).label('grade_a_count'),
        func.count().filter(Delivery.quality_grade == QualityGrade.B).label('grade_b_count'),
        func.count().filter(Delivery.quality_grade == QualityGrade.C).label('grade_c_count'),
        func.count().filter(Delivery.quality_grade == QualityGrade.REJECTED).label('rejected_count'),
    ).join(Station).filter(Delivery.delivery_date == report_date)
    
    if station_id:
        station_query = station_query.filter(Delivery.station_id == station_id)
    
    station_totals_data = station_query.group_by(Delivery.station_id, Station.name).all()
    
    # Farmer totals query
    farmer_query = db.query(
        Delivery.farmer_id,
        Farmer.farmer_code,
        Farmer.name.label('farmer_name'),
        func.count(Delivery.id).label('delivery_count'),
        func.sum(Delivery.quantity_liters).label('total_liters'),
        func.avg(Delivery.fat_content).label('avg_fat_content'),
    ).join(Farmer).filter(Delivery.delivery_date == report_date)
    
    if station_id:
        farmer_query = farmer_query.filter(Delivery.station_id == station_id)
    
    farmer_totals_data = farmer_query.group_by(
        Delivery.farmer_id, Farmer.farmer_code, Farmer.name
    ).all()
    
    # Build response
    station_totals = [
        DailyStationTotal(
            station_id=str(row.station_id),
            station_name=row.station_name,
            delivery_count=row.delivery_count,
            total_liters=row.total_liters or 0,
            avg_fat_content=row.avg_fat_content or 0,
            grade_a_count=row.grade_a_count or 0,
            grade_b_count=row.grade_b_count or 0,
            grade_c_count=row.grade_c_count or 0,
            rejected_count=row.rejected_count or 0,
        )
        for row in station_totals_data
    ]
    
    farmer_totals = [
        DailyFarmerTotal(
            farmer_id=str(row.farmer_id),
            farmer_code=row.farmer_code,
            farmer_name=row.farmer_name,
            delivery_count=row.delivery_count,
            total_liters=row.total_liters or 0,
            avg_fat_content=row.avg_fat_content or 0,
            quality_grades={}  # TODO: Add quality grade breakdown per farmer
        )
        for row in farmer_totals_data
    ]
    
    # Calculate overall totals
    overall_total_liters = sum(st.total_liters for st in station_totals)
    overall_delivery_count = sum(st.delivery_count for st in station_totals)
    
    return DailyReportResponse(
        date=report_date,
        station_totals=station_totals,
        farmer_totals=farmer_totals,
        overall_total_liters=overall_total_liters,
        overall_delivery_count=overall_delivery_count
    )


@router.get("/monthly", response_model=MonthlyReportResponse)
async def get_monthly_report(
    month: str = Query(..., pattern=r'^\d{4}-\d{2}$', description="Month in YYYY-MM format"),
    farmer_id: Optional[UUID] = Query(None, description="Filter by farmer"),
    db: Session = Depends(get_db),
    current_user: Officer = Depends(require_officer)
):
    """
    Get monthly aggregated report.
    
    Returns monthly summary including estimated payment calculation.
    
    **Required permissions:** Officer, Manager, or Admin
    
    **Example:** `/api/v1/reports/monthly?month=2025-10&farmer_id=<uuid>`
    """
    if not farmer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="farmer_id is required for monthly report"
        )
    
    # Parse month
    from datetime import datetime
    try:
        month_date = datetime.strptime(f"{month}-01", "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month format. Use YYYY-MM"
        )
    
    # Get or generate monthly summary
    summary = db.query(MonthlySummary).filter(
        MonthlySummary.farmer_id == farmer_id,
        MonthlySummary.month == month_date
    ).first()
    
    if not summary:
        # Generate summary on-the-fly
        from app.services.summary_service import generate_monthly_summary
        summary = generate_monthly_summary(db, farmer_id, month_date)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No deliveries found for farmer {farmer_id} in {month}"
        )
    
    # Get farmer info
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    
    farmer_summary = MonthlyFarmerSummary(
        farmer_id=str(summary.farmer_id),
        farmer_code=farmer.farmer_code,
        farmer_name=farmer.name,
        total_liters=summary.total_liters,
        total_deliveries=summary.total_deliveries,
        avg_fat_content=summary.avg_fat_content or 0,
        estimated_payment=summary.estimated_payment or 0,
        currency=summary.currency,
        grade_distribution={
            "A": summary.grade_a_count or 0,
            "B": summary.grade_b_count or 0,
            "C": summary.grade_c_count or 0,
            "Rejected": summary.rejected_count or 0,
        }
    )
    
    return MonthlyReportResponse(
        month=month,
        farmer_summary=farmer_summary,
        deliveries_by_grade=farmer_summary.grade_distribution,
        total_estimated_payment=summary.estimated_payment or 0,
        currency=summary.currency
    )
