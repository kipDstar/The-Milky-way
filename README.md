## Digital Dairy Collection & Payment Transparency System (DDCPTS)

Pilot-ready, scalable, secure fullstack platform for dairy collection, SMS transparency, and M-Pesa payment workflows.

### Tech stack (chosen)
- Backend: FastAPI (Python 3.11), SQLAlchemy, Alembic, Pydantic v2
- Database: PostgreSQL 15
- Web: React + TypeScript (Vite)
- Mobile: Flutter (offline-first with encrypted SQLite + sync worker)
- Messaging: SMS provider adapter (Africa's Talking primary; Twilio alternative)
- Payments: Safaricom Daraja (M-Pesa) B2C (sandbox-first)
- Infra: Docker, docker-compose for dev; Terraform skeleton for AWS (VPC, ECS Fargate, RDS Postgres, S3 backups)
- Observability: Sentry (errors), Prometheus /metrics
- CI: GitHub Actions

### Monorepo layout
```
/
├─ backend/ (FastAPI)
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ v1/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  └─ services/
│  ├─ sql/
│  ├─ tests/
│  ├─ Dockerfile
│  └─ requirements.txt
├─ mobile/ (Flutter)
├─ web/ (React + TypeScript)
├─ infra/
│  └─ terraform/
├─ .github/workflows/ci.yml
├─ docker-compose.yml
├─ README.md
├─ DEVELOPMENT_PLAN.md
├─ DECISIONS.md
├─ INTEGRATION_NOTES.md
├─ CHANGELOG.md
└─ .env.example
```

### Quickstart (local dev)
Prerequisites: Docker, Docker Compose, make (optional).

1) Copy environment template and adjust values as needed
```bash
cp .env.example .env
```

2) Start services (Postgres + Backend API)
```bash
docker compose up --build
```

3) API
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health
- Metrics (Prometheus): http://localhost:8000/metrics

4) Apply schema (dev)
The backend container applies `backend/sql/schema.sql` automatically on first run in dev. For production, Alembic migrations are provided (to be implemented in subsequent commits) and documented in `DEVELOPMENT_PLAN.md`.

### Security notes
- Do not commit real credentials. Use `.env` for local and a secret manager in production.
- JWT secrets, SMS and M-Pesa credentials must be set via environment variables.
- Rate limits enabled per IP/user; adjust via env vars.

### Documentation
- `DEVELOPMENT_PLAN.md`: modules and priorities
- `DECISIONS.md`: explicit assumptions and TODOs requiring product input
- `INTEGRATION_NOTES.md`: SMS and M-Pesa integration steps with official docs links
- `CHANGELOG.md`: high-level changes and tradeoffs

### Licensing & Compliance
This repository is for a pilot in Kenya. Ensure compliance with privacy regulations and Safaricom Daraja terms before enabling real payouts.

# The-Milky-way
Collection, records, payment and informational assistance application targeting milk collection process
