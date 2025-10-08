# Digital Dairy Collection & Payment Transparency System (DDCPTS)

A scalable, secure, and production-ready fullstack application for dairy collection management, payment transparency, and farmer empowerment in Kenya.

## 🎯 Project Overview

DDCPTS is designed to digitize and streamline dairy collection operations, providing:
- **Real-time milk delivery tracking** with SMS confirmations
- **Offline-first mobile app** for dairy officers in low-connectivity areas
- **Transparent payment processing** via M-Pesa integration
- **Quality grading and analytics** for operational insights
- **Farmer empowerment** through transparent communication

## 🏗️ Architecture

**Tech Stack:**
- **Backend**: FastAPI (Python 3.11+) with async/await
- **Database**: PostgreSQL 15+ with UUID support
- **Mobile**: Flutter 3.x (offline-first with SQLite sync)
- **Web**: React 18+ with TypeScript + Vite
- **SMS**: Africa's Talking (with adapter pattern for provider flexibility)
- **Payments**: Safaricom Daraja API (M-Pesa B2C)
- **Infrastructure**: Docker, AWS ECS/Fargate, Terraform
- **Monitoring**: Sentry (errors), Prometheus/Grafana (metrics)
- **CI/CD**: GitHub Actions

## 📁 Repository Structure

```
/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic (SMS, payments, sync)
│   │   ├── core/         # Config, security, dependencies
│   │   └── tests/        # Unit and integration tests
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── mobile/               # Flutter mobile app
│   ├── lib/
│   │   ├── models/       # Data models
│   │   ├── services/     # API client, sync service
│   │   ├── screens/      # UI screens
│   │   └── widgets/      # Reusable UI components
│   ├── test/
│   └── pubspec.yaml
├── web/                  # React web dashboard
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── utils/        # Helpers
│   ├── tests/
│   └── package.json
├── infra/                # Infrastructure as Code
│   ├── terraform/        # AWS infrastructure
│   └── k8s/              # Kubernetes manifests (optional)
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── docker-compose.yml    # Local development environment
├── .env.example          # Environment variable template
├── DEVELOPMENT_PLAN.md   # Implementation roadmap
├── DECISIONS.md          # Architectural decisions & TODOs
├── INTEGRATION_NOTES.md  # Third-party integration guides
├── CHANGELOG.md          # Version history
└── README.md             # This file
```

## 🚀 Quick Start (Local Development)

### Prerequisites

- Docker 24+ and Docker Compose
- Git
- (Optional) Python 3.11+, Node 18+, Flutter 3.x for local development

### 1. Clone and Configure

```bash
git clone <repository-url>
cd ddcpts

# Copy environment template and configure
cp .env.example .env
# Edit .env with your configuration (see below)
```

### 2. Start All Services with Docker Compose

```bash
# Build and start all services (backend, database, web)
docker-compose up --build

# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Web Dashboard: http://localhost:3000
# Database: localhost:5432
```

### 3. Run Database Migrations

```bash
# In a new terminal
docker-compose exec backend alembic upgrade head

# Seed initial data (creates test users, stations, farmers)
docker-compose exec backend python -m app.scripts.seed_data
```

### 4. Access the System

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Web Dashboard**: http://localhost:3000
  - Default admin login: `admin@ddcpts.test` / `Admin@123` (change immediately)
- **PostgreSQL**: `localhost:5432` (user: `ddcpts`, db: `ddcpts_dev`)

### 5. Mobile App Development

```bash
cd mobile

# Install dependencies
flutter pub get

# Run on emulator/device
flutter run

# Run tests
flutter test
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://ddcpts:password@localhost:5432/ddcpts_dev

# Security
SECRET_KEY=<generate-strong-random-key>  # openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMS Provider (Africa's Talking)
SMS_PROVIDER=africastalking
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=<your-sandbox-key>
AFRICASTALKING_SENDER_ID=DDCPTS

# M-Pesa (Safaricom Daraja - Sandbox)
MPESA_ENVIRONMENT=sandbox  # or 'production'
MPESA_CONSUMER_KEY=<your-consumer-key>
MPESA_CONSUMER_SECRET=<your-consumer-secret>
MPESA_SHORTCODE=<your-shortcode>
MPESA_PASSKEY=<your-passkey>
ENABLE_REAL_PAYMENTS=false  # MUST be false until production ready

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
ENABLE_METRICS=true

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
```

### Getting API Keys

**Africa's Talking (SMS):**
1. Sign up at https://account.africastalking.com/auth/register
2. Get sandbox API key from https://account.africastalking.com/apps/sandbox
3. Sandbox allows 100 free messages/day
4. Official docs: https://developers.africastalking.com/docs/sms/overview

**Safaricom Daraja (M-Pesa):**
1. Register at https://developer.safaricom.co.ke/
2. Create a sandbox app to get Consumer Key and Secret
3. Follow sandbox guide: https://developer.safaricom.co.ke/APIs/MobileMoney
4. **IMPORTANT**: Real payments require business approval and setup

## 🧪 Testing

### Backend Tests

```bash
# Run all tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest app/tests/test_deliveries.py -v

# View coverage report
open backend/htmlcov/index.html
```

### Web Tests

```bash
cd web

# Unit tests
npm test

# E2E tests (Playwright)
npm run test:e2e

# Coverage
npm run test:coverage
```

### Mobile Tests

```bash
cd mobile

# Unit tests
flutter test

# Integration tests
flutter test integration_test/
```

## 📊 Database Management

### Migrations

```bash
# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

### Backup & Restore

```bash
# Backup database
docker-compose exec db pg_dump -U ddcpts ddcpts_dev > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U ddcpts ddcpts_dev < backup_20251008.sql
```

See `docs/ADMIN_PLAYBOOK.md` for production backup procedures.

## 🚢 Deployment

### AWS Deployment (Production)

See `infra/terraform/README.md` for detailed deployment instructions.

**Quick overview:**

1. **Prerequisites**: AWS CLI configured, Terraform installed
2. **Infrastructure setup**:
   ```bash
   cd infra/terraform
   terraform init
   terraform plan -var-file=production.tfvars
   # Review plan carefully
   terraform apply -var-file=production.tfvars
   ```
3. **Database migrations**: Run via ECS task
4. **Monitoring setup**: Configure Sentry, CloudWatch, Prometheus

### CI/CD Pipeline

GitHub Actions automatically:
- Runs linting and type checks
- Executes unit and integration tests
- Builds Docker images
- Pushes to AWS ECR (on main branch)
- Deploys to staging (on main branch)
- Deploys to production (on version tags)

## 📖 API Documentation

### OpenAPI Specification

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Postman Collection

Import `postman/DDCPTS_API.postman_collection.json` into Postman for pre-configured API requests with examples.

## 🔐 Security

- **Authentication**: JWT with access + refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Password hashing**: Argon2 (OWASP recommended)
- **Rate limiting**: Configured per endpoint
- **TLS**: Required in production (enforced by infrastructure)
- **PII protection**: Sensitive data masked in logs
- **Audit trail**: All critical operations logged

See `docs/SECURITY.md` for security best practices and incident response.

## 📚 Documentation

- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)**: Implementation roadmap and priorities
- **[DECISIONS.md](DECISIONS.md)**: Architectural decisions and trade-offs
- **[INTEGRATION_NOTES.md](INTEGRATION_NOTES.md)**: Third-party integration guides
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and changes
- **[docs/ADMIN_PLAYBOOK.md](docs/ADMIN_PLAYBOOK.md)**: Operations guide for admins
- **[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)**: API request/response examples

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Follow code style guidelines (enforced by linters)
3. Write tests for new functionality
4. Update documentation as needed
5. Commit with clear messages: `git commit -m "feat: add farmer bulk import"`
6. Push and create a Pull Request

## 📝 License

[Specify license - e.g., MIT, Apache 2.0]

## 🆘 Support & Troubleshooting

### Common Issues

**Database connection failed:**
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check DATABASE_URL in `.env` matches docker-compose.yml

**SMS not sending:**
- Verify Africa's Talking credentials in `.env`
- Check sandbox account has credits
- Review `sms_logs` table for error messages

**Mobile app sync issues:**
- Ensure backend is accessible from mobile device
- Check API URL in mobile app config
- Review sync logs in app settings

### Getting Help

- Check existing issues: https://github.com/[org]/ddcpts/issues
- Create new issue using provided templates
- For security issues: email security@[domain]

## 🗺️ Roadmap

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed roadmap.

**Current Phase**: MVP (v0.1.0)
- ✅ Core farmer and delivery management
- ✅ SMS confirmations
- ✅ Offline-first mobile app
- 🔄 M-Pesa payment integration
- 🔄 Web dashboard analytics

**Next Phase**: Pilot Ready (v0.2.0)
- Payment automation
- Advanced analytics and reporting
- Farmer feedback system
- Bulk data import tools

---

**Built with ❤️ for Kenyan dairy farmers and cooperatives**
