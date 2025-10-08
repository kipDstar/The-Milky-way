from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_farmer():
    return {"id": "TODO"}

@router.get("/{farmer_code}")
async def get_farmer(farmer_code: str):
    return {"farmer_code": farmer_code, "deliveries": []}

