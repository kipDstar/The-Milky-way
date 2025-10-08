from fastapi import APIRouter

router = APIRouter()

@router.post("/batch")
async def sync_batch():
    return {"results": []}
