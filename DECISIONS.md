## Decisions & Assumptions

1) Tech stack: FastAPI + PostgreSQL + React + Flutter per specification; chosen for strong typing, OpenAPI support, and portability.
2) Phone normalization: Use E.164 via `phonenumbers` library. Kenya default region KE if country code missing.
3) Quantity limits: Default 0 < liters <= 200; configurable via env `DELIVERY_MAX_LITERS`.
4) Payment estimation formula: TODO: Product input required for per-liter rate, bonuses, deductions. Placeholder env `PAY_RATE_PER_LITER` used in monthly estimates.
5) OTP provider: Leverage same SMS adapter; OTP TTL 5 minutes; rate limited by IP and user.
6) PII logging: Mask phone and national_id in application logs; full values only in `audit_logs` with restricted access.
7) Timezone: All server timestamps in UTC; `delivery_date` stored as local date string (station locale); assume Africa/Nairobi for Kenya stations.
8) Conflict policy (mobile sync): Last-write-wins by default with explicit conflict flag; manual resolution path exposed via API.
9) Multi-company support: `stations.company` string used for scoping; full multi-tenant isolation is a future enhancement.

TODOs requiring product input
- Define payment rate rules and adjustments beyond flat per-liter rate.
- Define SMS sender ID and message signature policy.
- Define station-company authorization boundaries (cross-station visibility rules for managers).

