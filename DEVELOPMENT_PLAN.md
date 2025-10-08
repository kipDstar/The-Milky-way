# Development Plan

## Overview

This document outlines the implementation roadmap for the Digital Dairy Collection & Payment Transparency System (DDCPTS). The plan is organized by priority phases aligned with MVP delivery and iterative value delivery.

## Guiding Principles

1. **MVP First**: Deliver core value early - farmer registration, delivery tracking, SMS confirmations
2. **Iterative Enhancement**: Add complexity progressively - payments, analytics, advanced features
3. **Quality Gates**: Each module requires tests, documentation, and security review before merge
4. **Modular Design**: Components must be independently testable and deployable
5. **Real-world Constraints**: Design for low connectivity, SMS reliability issues, and scale

## Phase 1: Foundation & MVP (Weeks 1-4)

### 1.1 Infrastructure & Development Environment
- [x] Repository structure and monorepo setup
- [x] Docker Compose for local development
- [x] PostgreSQL database setup with connection pooling
- [x] CI/CD pipeline (GitHub Actions) - lint, test, build
- [x] Environment configuration management (.env, secrets)

### 1.2 Database Schema & Migrations
- [x] Core tables: farmers, stations, officers, deliveries
- [x] Supporting tables: monthly_summaries, payments, sms_logs, audit_logs
- [x] SQLAlchemy ORM models with relationships
- [x] Alembic migration scripts
- [x] Seed data scripts for development and testing

### 1.3 Backend API - Core Features
- [x] FastAPI application structure with dependency injection
- [x] Authentication & Authorization:
  - JWT access and refresh tokens
  - Password hashing (Argon2)
  - Role-based access control (RBAC)
  - OTP 2FA support (skeleton)
- [x] Farmer Management:
  - POST /api/v1/farmers (create farmer with validation)
  - GET /api/v1/farmers/{farmer_code} (profile + recent deliveries)
  - PUT /api/v1/farmers/{id} (update farmer info)
  - GET /api/v1/farmers (list with pagination, search, filters)
- [x] Delivery Management:
  - POST /api/v1/deliveries (create delivery, trigger SMS)
  - GET /api/v1/deliveries (list with filters, pagination)
  - GET /api/v1/deliveries/{id} (delivery detail)
  - Quality validation (grade, quantity limits)
- [x] OpenAPI specification generation at /openapi.json
- [x] Pydantic schemas for request/response validation
- [x] Error handling with consistent JSON error responses

### 1.4 SMS Integration
- [x] SMS adapter interface (SMSProvider abstract class)
- [x] Africa's Talking concrete adapter implementation
- [x] Mock SMS provider for testing
- [x] SMS templates:
  - Delivery confirmation (English + Swahili)
  - Monthly summary (English + Swahili)
  - Rejection notification
- [x] Asynchronous SMS sending with queue (background tasks)
- [x] SMS logging to `sms_logs` table with status tracking
- [x] Retry mechanism for failed SMS sends
- [x] Integration testing with Africa's Talking sandbox

### 1.5 Mobile App - MVP
- [x] Flutter project structure (clean architecture)
- [x] Offline-first architecture with SQLite local storage
- [x] Screens:
  - Login (officer authentication)
  - Farmer search/selection
  - Delivery entry form (quantity, quality, remarks)
  - Delivery history (local + synced)
  - Sync status indicator
- [x] Local delivery queue for offline operation
- [x] Automatic sync when connectivity restored
- [x] Conflict detection and resolution UI
- [x] API client with retry logic
- [x] Unit tests for services and models

### 1.6 Web Dashboard - MVP
- [x] React + TypeScript + Vite setup
- [x] Authentication (login, logout, token management)
- [x] Officer role:
  - Farmer registration form
  - Delivery entry (web-based alternative to mobile)
  - Daily delivery list view
- [x] Manager role:
  - Daily reports (totals by station, by farmer)
  - Delivery search and filters
  - SMS status monitoring
- [x] Responsive design (mobile-first)
- [x] API client with error handling
- [x] Component tests (React Testing Library)

### 1.7 Testing & Quality Assurance
- [x] Backend unit tests (models, schemas, utilities) - Target: 80% coverage
- [x] Backend integration tests (API endpoints with test DB)
- [x] Mobile unit tests (models, services)
- [x] Mobile integration tests (offline sync flow)
- [x] Web unit tests (components, services)
- [x] Web E2E tests (Playwright - login, create farmer, create delivery)
- [x] Linting and type checking in CI
- [x] Test coverage reporting

## Phase 2: Payments & Advanced Features (Weeks 5-7)

### 2.1 M-Pesa Daraja Integration
- [ ] Payment adapter interface (PaymentProvider)
- [ ] Safaricom Daraja API client
  - OAuth token management
  - B2C payment disbursement endpoint
  - Transaction status query
  - Callback handling (result and timeout URLs)
- [ ] Sandbox mode implementation (ENABLE_REAL_PAYMENTS=false by default)
- [ ] Payment batch processing:
  - POST /api/v1/payments/disburse (batch monthly payments)
  - Job queue for async payment processing
  - Payment status tracking in `payments` table
- [ ] Payment reconciliation:
  - Match Daraja callbacks to internal payment records
  - Handle failed payments (retry logic, manual intervention)
- [ ] Mock payment provider for testing
- [ ] Integration tests with Daraja sandbox
- [ ] Documentation: INTEGRATION_NOTES.md section on M-Pesa setup

### 2.2 Monthly Summaries & Reporting
- [ ] Scheduled job (cron/Celery) to generate monthly summaries
  - Aggregate deliveries by farmer and month
  - Calculate estimated payment (configurable pricing formula)
  - Store in `monthly_summaries` table
  - Send monthly summary SMS to farmers
- [ ] API endpoints:
  - GET /api/v1/reports/monthly?farmer_id=&month= (farmer view)
  - GET /api/v1/reports/monthly?station_id=&month= (station totals)
  - GET /api/v1/reports/annual?year= (yearly trends)
- [ ] Web dashboard enhancements:
  - Monthly summary view with charts
  - Payment history per farmer
  - Export reports to CSV/PDF
- [ ] Background job monitoring and error alerting

### 2.3 Analytics & Dashboard Enhancements
- [ ] API endpoints:
  - GET /api/v1/analytics/daily-trends (time series data)
  - GET /api/v1/analytics/top-farmers (leaderboard)
  - GET /api/v1/analytics/quality-distribution (grade breakdown)
  - GET /api/v1/analytics/station-performance (comparative metrics)
- [ ] Web dashboard charts (Chart.js or Recharts):
  - Daily delivery volume trends
  - Quality grade distribution
  - Top farmers by volume
  - Station comparison
- [ ] Real-time dashboard updates (WebSocket or polling)
- [ ] Date range filters and export capabilities

### 2.4 Farmer Feedback System
- [ ] Database table: `farmer_feedback`
  - farmer_id, delivery_id (optional), rating, comment, category, created_at
- [ ] API endpoints:
  - POST /api/v1/feedback (submit feedback via SMS or web)
  - GET /api/v1/feedback (manager/admin view with filters)
  - PATCH /api/v1/feedback/{id} (mark as resolved)
- [ ] SMS-based feedback collection:
  - Inbound SMS handler (webhook from Africa's Talking)
  - Parse feedback keywords and store
- [ ] Web interface for reviewing feedback
- [ ] Feedback analytics (sentiment trends)

### 2.5 Bulk Data Import
- [ ] CSV upload endpoint: POST /api/v1/import/deliveries
  - File validation (schema check)
  - Preview import with error detection
  - Batch insert with transaction safety
  - Import job status tracking
- [ ] Web UI for upload and preview
- [ ] Support for historical data migration
- [ ] Import audit trail

## Phase 3: Production Readiness (Weeks 8-10)

### 3.1 Infrastructure as Code (Terraform)
- [ ] AWS infrastructure modules:
  - VPC with public/private subnets
  - RDS PostgreSQL (Multi-AZ for production)
  - ECS cluster with Fargate tasks
  - Application Load Balancer
  - ECR for Docker images
  - S3 bucket for backups and static assets
  - CloudWatch log groups
  - Secrets Manager for sensitive config
  - IAM roles and security groups
- [ ] Terraform environments: development, staging, production
- [ ] Terraform state backend (S3 + DynamoDB locking)
- [ ] Documentation: infra/terraform/README.md

### 3.2 Monitoring & Observability
- [ ] Sentry integration:
  - Backend error tracking
  - Frontend error tracking (web + mobile)
  - Performance monitoring
  - Release tracking
- [ ] Prometheus metrics:
  - /metrics endpoint (FastAPI with prometheus_client)
  - Custom metrics: delivery_count, sms_sent, api_latency
  - HTTP request metrics
- [ ] Grafana dashboards (via docker-compose or AWS Managed Grafana):
  - API performance
  - Delivery volumes
  - SMS success rates
  - Database metrics
- [ ] Structured logging:
  - JSON log format
  - Request ID tracing
  - PII masking in logs
- [ ] Health check endpoints:
  - /health (liveness)
  - /health/ready (readiness - DB connection, external services)

### 3.3 Security Hardening
- [ ] Rate limiting:
  - Per-IP and per-user limits
  - Endpoint-specific limits (e.g., stricter on auth endpoints)
  - Redis-backed rate limiter
- [ ] TLS enforcement:
  - HTTPS only in production
  - Certificate management (Let's Encrypt or ACM)
- [ ] Security headers (FastAPI middleware):
  - HSTS, X-Content-Type-Options, X-Frame-Options, CSP
- [ ] Input sanitization and SQL injection prevention (ORM handles most)
- [ ] CORS configuration (whitelist known origins)
- [ ] Secrets rotation procedures documented
- [ ] Security audit and penetration testing (external or automated tools)
- [ ] GDPR/data privacy compliance review (for PII handling)

### 3.4 Database Optimization
- [ ] Indexing strategy review:
  - deliveries(farmer_id, delivery_date)
  - deliveries(station_id, delivery_date)
  - farmers(farmer_code)
  - sms_logs(farmer_id, sent_at)
- [ ] Query performance testing and optimization
- [ ] Connection pooling tuning
- [ ] Database backup automation:
  - Daily backups to S3
  - Point-in-time recovery setup (RDS)
  - Backup restore testing
  - Retention policy (30 days rolling, monthly archives for 1 year)
- [ ] Database monitoring (slow query log, connection stats)

### 3.5 CI/CD Enhancements
- [ ] GitHub Actions workflows:
  - Lint and typecheck (on PR)
  - Unit tests (on PR)
  - Integration tests with Docker Compose (on PR)
  - Build and push Docker images (on main merge)
  - Deploy to staging (on main merge)
  - Deploy to production (on version tag with manual approval)
- [ ] Automated security scanning (Snyk, Dependabot)
- [ ] Deployment smoke tests (post-deploy health checks)
- [ ] Rollback procedures documented

### 3.6 Documentation & Operations
- [ ] Admin Playbook (docs/ADMIN_PLAYBOOK.md):
  - Running monthly payouts
  - Resolving payment failures
  - Database backup and restore procedures
  - SMS delivery troubleshooting
  - Key rotation procedures
  - Incident response runbook
  - Scaling procedures
- [ ] API Examples (docs/API_EXAMPLES.md):
  - Full request/response examples for all endpoints
  - Error response examples
  - Authentication flow examples
- [ ] Postman collection with pre-request scripts and tests
- [ ] Integration guides (INTEGRATION_NOTES.md):
  - Africa's Talking setup (sandbox -> production)
  - Safaricom Daraja setup (sandbox -> production)
  - Required approvals and credentials
- [ ] CHANGELOG.md maintenance
- [ ] Versioning strategy (Semantic Versioning)

## Phase 4: Long-term Enhancements (Post-Launch)

### 4.1 Advanced Analytics
- [ ] Predictive analytics:
  - Forecast monthly delivery volumes
  - Identify at-risk farmers (declining deliveries)
- [ ] Quality trend analysis (farmer improvement over time)
- [ ] Station efficiency metrics
- [ ] Custom report builder for managers

### 4.2 Multi-language Support
- [ ] i18n framework for web and mobile
- [ ] Swahili translations (priority)
- [ ] Additional regional languages (based on demand)
- [ ] SMS templates in multiple languages

### 4.3 Farmer Self-Service Portal
- [ ] Web portal for farmers:
  - View delivery history
  - View payment history
  - Submit feedback
  - Update contact information
- [ ] USSD integration (for feature phones)

### 4.4 Integration Expansions
- [ ] Additional payment providers (Airtel Money, Tkash)
- [ ] Additional SMS providers (Twilio as fallback)
- [ ] Accounting software integration (export to QuickBooks, Xero)
- [ ] Cold chain monitoring integration (temperature sensors)

### 4.5 Scalability & Performance
- [ ] Database sharding strategy (for >1M farmers)
- [ ] Read replicas for analytics queries
- [ ] Caching layer (Redis for frequently accessed data)
- [ ] CDN for static assets
- [ ] Horizontal scaling of API servers (auto-scaling groups)

### 4.6 Machine Learning Features
- [ ] Fraud detection (unusual delivery patterns)
- [ ] Quality prediction based on historical data and external factors
- [ ] Optimal pricing recommendations
- [ ] Churn prediction and farmer retention strategies

## Testing Strategy

### Unit Tests
- Target: 80% code coverage minimum
- All business logic functions
- Model validations
- Utility functions

### Integration Tests
- API endpoint flows with test database
- SMS sending flow (mock provider + real sandbox)
- Payment flow (mock provider + sandbox)
- Database transaction integrity

### End-to-End Tests
- Web: Playwright tests for critical user flows
- Mobile: Flutter integration tests
- Complete flows: Register farmer → Create delivery → Receive SMS → View report

### Performance Tests
- Load testing with k6 or Locust
- Target: 100 req/s sustained on single API instance
- Database query performance benchmarks

### Security Tests
- OWASP ZAP automated scanning
- SQL injection prevention verification
- XSS prevention verification
- Authentication bypass attempts

## Quality Gates

Before merging any feature:
1. ✅ All tests pass (unit, integration, E2E where applicable)
2. ✅ Code coverage meets minimum threshold
3. ✅ Linting and type checking pass
4. ✅ Security review completed (for sensitive features)
5. ✅ Documentation updated (API docs, README, inline comments)
6. ✅ PR review by at least one other developer
7. ✅ Manual testing in local/staging environment

## Success Metrics

### MVP Success (Phase 1)
- [ ] 100% of core API endpoints implemented and documented
- [ ] Mobile app successfully records deliveries offline and syncs
- [ ] SMS confirmations sent within 10 seconds of delivery entry
- [ ] Web dashboard displays accurate daily totals
- [ ] Zero critical security vulnerabilities
- [ ] 80%+ test coverage on backend

### Pilot Ready (Phase 2)
- [ ] Monthly payment batch successfully processed in sandbox
- [ ] Analytics dashboard provides actionable insights
- [ ] System handles 1,000 deliveries/day with <1s avg API response time
- [ ] 99% SMS delivery success rate
- [ ] Farmer feedback system operational

### Production Ready (Phase 3)
- [ ] Infrastructure fully automated (Terraform)
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery tested and documented
- [ ] Security audit completed with no high-severity issues
- [ ] Load testing passed (10,000 deliveries/day)
- [ ] Operations runbooks complete

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SMS provider downtime | High | Implement retry logic, queue messages, provide fallback provider |
| M-Pesa API issues | High | Sandbox testing, comprehensive error handling, manual fallback process |
| Database data loss | Critical | Automated daily backups, point-in-time recovery, backup restore testing |
| Offline sync conflicts | Medium | Clear conflict resolution UI, deterministic merge rules, audit trail |
| Low mobile connectivity | High | Offline-first design, sync compression, incremental sync |
| API credential exposure | Critical | Secrets manager, key rotation procedures, environment separation |
| Scaling bottlenecks | Medium | Performance testing early, horizontal scaling ready, caching strategy |

## Dependencies & External Services

| Service | Purpose | Sandbox Available | Docs |
|---------|---------|-------------------|------|
| Africa's Talking | SMS delivery | Yes | https://developers.africastalking.com/ |
| Safaricom Daraja | M-Pesa payments | Yes | https://developer.safaricom.co.ke/ |
| Sentry | Error tracking | Yes (free tier) | https://docs.sentry.io/ |
| AWS | Infrastructure | Yes | https://docs.aws.amazon.com/ |

## Assumptions & Decisions

Documented in [DECISIONS.md](DECISIONS.md) including:
- Pricing formula for payment calculation (configurable)
- Conflict resolution rules for offline sync
- Data retention policies
- SMS character limits and message chunking
- Payment batch processing schedule

---

**Last Updated**: 2025-10-08  
**Next Review**: Upon completion of Phase 1
