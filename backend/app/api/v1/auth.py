from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"access_token": "TODO", "refresh_token": "TODO"}

@router.post("/otp-send")
async def otp_send():
    return {"status": "queued"}

@router.post("/verify-otp")
async def verify_otp():
    return {"access_token": "TODO", "refresh_token": "TODO"}

