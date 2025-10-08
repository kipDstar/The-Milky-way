from .base import PaymentsProvider
from typing import Any, Dict

class MockPaymentsProvider(PaymentsProvider):
    async def disburse_b2c(self, entries: list[Dict[str, Any]], sandbox: bool = True) -> Dict[str, Any]:
        return {"job_id": "mock-job", "status": "queued", "sandbox": sandbox}
