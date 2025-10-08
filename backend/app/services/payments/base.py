from abc import ABC, abstractmethod
from typing import Any, Dict

class PaymentsProvider(ABC):
    @abstractmethod
    async def disburse_b2c(self, entries: list[Dict[str, Any]], sandbox: bool = True) -> Dict[str, Any]:
        raise NotImplementedError
