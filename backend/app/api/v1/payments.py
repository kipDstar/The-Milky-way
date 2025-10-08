from fastapi import APIRouter

router = APIRouter()

@router.post("/disburse")
async def disburse_payments(month: str, sandbox: bool = True):
    return {"job_id": "TODO", "status": "queued", "sandbox": sandbox}

