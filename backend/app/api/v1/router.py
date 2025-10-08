from fastapi import APIRouter

from . import auth, farmers, deliveries, reports, payments, sync

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])

