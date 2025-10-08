## Development Plan

### MVP (Pilot)
- Backend FastAPI service with core entities and endpoints
- PostgreSQL schema and seed data
- SMS adapter interface + Africa's Talking implementation (sandbox)
- Delivery flow: create delivery -> queue SMS -> log status
- Manager reports: daily totals, monthly summaries (API + minimal web UI)
- JWT auth + roles (officer, manager, admin) + optional 2FA OTP via SMS
- OpenAPI docs, Postman collection
- Docker-compose dev environment, GitHub Actions CI
- Basic observability: Sentry placeholder, /metrics
- Backup scripts (pg_dump to local/S3 stub)

### Near-term
- M-Pesa Daraja B2C sandbox adapter with strict `sandbox=true` and `ENABLE_REAL_PAYMENTS` flag
- Flutter mobile app with offline encrypted store and sync worker
- Web app UI (React+TS) for officer entry and manager dashboards
- Alembic migrations end-to-end and migration tooling
- Rate limiting policies, audit logs expansion, PII redaction helper
- E2E tests (Cypress) and mobile integration tests

### Long-term
- Cloud IaC for AWS (VPC, ECS Fargate, RDS, S3, CloudWatch, ALB)
- Prometheus + Grafana stack
- Advanced analytics (TimescaleDB)
- Multi-tenant support (company/station scoping)
- Conflict resolution UX on mobile, richer reconciliation tooling

### Modules
- Auth: OAuth2 password + refresh, OTP, JWT
- Farmers: CRUD, validation, phone normalization
- Deliveries: create/list, validation, SMS queuing, audit logs
- Reports: daily and monthly summaries
- Payments: batch disburse (sandbox), payments ledger
- SMS: provider adapters, status checks, templating (i18n en/sw)
- Sync: `POST /api/v1/sync/batch` with compression and per-record status
- Observability: logging, metrics, error tracking
- Infra/CI: docker, compose, Terraform skeleton, GitHub Actions

