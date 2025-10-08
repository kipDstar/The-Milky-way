from abc import ABC, abstractmethod
from typing import Any, Dict

class SMSProvider(ABC):
    @abstractmethod
    async def send_sms(self, phone: str, message: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def check_status(self, provider_id: str) -> Dict[str, Any]:
        raise NotImplementedError
