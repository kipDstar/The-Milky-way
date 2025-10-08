"""Report schemas."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import date
from decimal import Decimal


class DailyStationTotal(BaseModel):
    """Daily totals for a station."""
    station_id: str
    station_name: str
    delivery_count: int
    total_liters: Decimal
    avg_fat_content: Decimal
    grade_a_count: int
    grade_b_count: int
    grade_c_count: int
    rejected_count: int


class DailyFarmerTotal(BaseModel):
    """Daily totals for a farmer."""
    farmer_id: str
    farmer_code: str
    farmer_name: str
    delivery_count: int
    total_liters: Decimal
    avg_fat_content: Decimal
    quality_grades: Dict[str, int]


class DailyReportResponse(BaseModel):
    """Daily report response."""
    date: date
    station_totals: List[DailyStationTotal]
    farmer_totals: List[DailyFarmerTotal]
    overall_total_liters: Decimal
    overall_delivery_count: int


class MonthlyFarmerSummary(BaseModel):
    """Monthly summary for a farmer."""
    farmer_id: str
    farmer_code: str
    farmer_name: str
    total_liters: Decimal
    total_deliveries: int
    avg_fat_content: Decimal
    estimated_payment: Decimal
    currency: str
    grade_distribution: Dict[str, int]


class MonthlyReportResponse(BaseModel):
    """Monthly report response."""
    month: str  # YYYY-MM
    farmer_summary: MonthlyFarmerSummary
    deliveries_by_grade: Dict[str, int]
    total_estimated_payment: Decimal
    currency: str
