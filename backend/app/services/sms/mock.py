from .base import SMSProvider
from typing import Any, Dict

class MockSMSProvider(SMSProvider):
    async def send_sms(self, phone: str, message: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"provider": "mock", "provider_id": "mock-123", "status": "sent"}

    async def check_status(self, provider_id: str) -> Dict[str, Any]:
        return {"status": "delivered"}
