from fastapi import APIRouter
from . import auth, farmers, deliveries, reports, payments, sync

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
router.include_router(payments.router, prefix="/payments", tags=["payments"])
router.include_router(sync.router, prefix="/sync", tags=["sync"])
