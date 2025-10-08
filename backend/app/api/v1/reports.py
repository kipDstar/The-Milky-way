from fastapi import APIRouter

router = APIRouter()

@router.get("/daily")
async def daily_report(station_id: str | None = None, date: str | None = None):
    return {"station_totals": {}, "by_farmer": []}

@router.get("/monthly")
async def monthly_report(farmer_id: str, month: str):
    return {"farmer_id": farmer_id, "month": month, "total_liters": 0, "estimated_payment": 0, "currency": "KES"}

