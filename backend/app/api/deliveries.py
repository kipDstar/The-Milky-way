from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_delivery():
    return {"id": "TODO", "sms_sent": False}

@router.get("")
async def list_deliveries():
    return {"items": [], "total": 0}
