from fastapi import APIRouter

router = APIRouter()

@router.get("/daily")
async def daily_report():
    return {"totals": []}

@router.get("/monthly")
async def monthly_report():
    return {"summary": {}}
