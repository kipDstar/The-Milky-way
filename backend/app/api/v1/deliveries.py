from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_delivery():
    return {"id": "TODO", "sms_sent": False}

@router.get("")
async def list_deliveries(station_id: str | None = None, date: str | None = None, page: int = 1, page_size: int = 50):
    return {"items": [], "page": page, "page_size": page_size, "total": 0}

