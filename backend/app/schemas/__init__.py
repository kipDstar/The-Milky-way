"""
Pydantic schemas for request/response validation.

Schemas define the structure of API requests and responses,
providing validation and documentation.
"""

from app.schemas.farmer import (
    FarmerBase,
    FarmerCreate,
    FarmerUpdate,
    FarmerResponse,
    FarmerWithRecentDeliveries,
)
from app.schemas.delivery import (
    DeliveryBase,
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryResponse,
    DeliveryWithRelations,
)
from app.schemas.officer import (
    OfficerBase,
    OfficerCreate,
    OfficerUpdate,
    OfficerResponse,
)
from app.schemas.station import (
    StationBase,
    StationCreate,
    StationUpdate,
    StationResponse,
)
from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentDisburseRequest,
)
from app.schemas.auth import (
    TokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    OTPSendRequest,
    OTPVerifyRequest,
)
from app.schemas.report import (
    DailyReportResponse,
    MonthlyReportResponse,
)

__all__ = [
    # Farmer
    "FarmerBase",
    "FarmerCreate",
    "FarmerUpdate",
    "FarmerResponse",
    "FarmerWithRecentDeliveries",
    # Delivery
    "DeliveryBase",
    "DeliveryCreate",
    "DeliveryUpdate",
    "DeliveryResponse",
    "DeliveryWithRelations",
    # Officer
    "OfficerBase",
    "OfficerCreate",
    "OfficerUpdate",
    "OfficerResponse",
    # Station
    "StationBase",
    "StationCreate",
    "StationUpdate",
    "StationResponse",
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    # Payment
    "PaymentCreate",
    "PaymentResponse",
    "PaymentDisburseRequest",
    # Auth
    "TokenResponse",
    "LoginRequest",
    "RefreshTokenRequest",
    "OTPSendRequest",
    "OTPVerifyRequest",
    # Report
    "DailyReportResponse",
    "MonthlyReportResponse",
]
