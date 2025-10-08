from fastapi import APIRouter

router = APIRouter()

@router.post("/disburse")
async def disburse_payments():
    return {"job_id": "TODO", "status": "queued"}
