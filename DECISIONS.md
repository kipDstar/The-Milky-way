# Architectural Decisions & Product Assumptions

This document captures key architectural decisions, product assumptions, and open TODOs requiring product owner input.

## Technology Stack Decisions

### 1. Backend: FastAPI (Python)

**Decision**: Use FastAPI with Python 3.11+

**Rationale**:
- **Excellent async/await support**: Critical for handling concurrent SMS and payment API calls without blocking
- **Built-in OpenAPI generation**: Automatic Swagger docs from code, reducing documentation drift
- **Type safety with Pydantic**: Request/response validation with clear error messages
- **Performance**: Comparable to Node.js for I/O-bound operations (which dominate this system)
- **Rich ecosystem**: SQLAlchemy, Alembic, Celery for background jobs, extensive payment/SMS libraries
- **Developer experience**: Clear, readable code; excellent for team scaling

**Alternatives considered**:
- NestJS (TypeScript): Excellent choice but Python has better ML/analytics libraries for future enhancements
- Django: Too opinionated; FastAPI gives better control for custom business logic

### 2. Database: PostgreSQL 15+

**Decision**: PostgreSQL with UUID primary keys and JSON support

**Rationale**:
- **ACID compliance**: Critical for financial transactions
- **UUID support**: Enables offline-first mobile (client-generated IDs) without collision risk
- **JSONB for flexible data**: Useful for audit logs and evolving payment metadata
- **Mature ecosystem**: Proven at scale, excellent backup/restore tools
- **Cost-effective**: Open source, managed services available (AWS RDS, GCP Cloud SQL)

**Schema decisions**:
- UUIDs for all primary keys (not serial integers) to support distributed ID generation
- Timestamps with timezone for all temporal data
- Soft deletes via `is_active` flag (retain historical data)
- Separate audit_logs table for compliance

### 3. Mobile: Flutter

**Decision**: Flutter for cross-platform mobile app

**Rationale**:
- **Single codebase**: iOS + Android from one codebase reduces development/maintenance cost
- **Offline-first capability**: Excellent local database support (sqflite, drift)
- **Performance**: Near-native performance suitable for data entry workflows
- **UI flexibility**: Material Design components, easy customization
- **Active ecosystem**: Good package availability for HTTP, local storage, background sync

**Alternatives considered**:
- React Native: Good choice but Flutter's offline story is stronger
- Native (Swift/Kotlin): Best performance but doubles development effort

### 4. Web: React + TypeScript + Vite

**Decision**: React 18 with TypeScript and Vite bundler

**Rationale**:
- **React**: Industry standard, excellent developer pool, rich ecosystem
- **TypeScript**: Type safety reduces runtime errors, improves refactoring confidence
- **Vite**: Fast dev server, optimized builds, better DX than Create React App
- **Future-ready**: Easy migration to Next.js if SSR/SSG needed later

### 5. SMS Provider: Africa's Talking (with adapter pattern)

**Decision**: Default to Africa's Talking but implement provider-agnostic adapter

**Rationale**:
- **Regional focus**: Africa's Talking is optimized for African carriers, better delivery rates in Kenya
- **Sandbox support**: Free sandbox for development and testing
- **Cost-effective**: Competitive pricing for high-volume SMS
- **Adapter pattern**: Easy to swap to Twilio, Safaricom, or others without code changes

**Provider adapter interface**:
```python
class SMSProvider(ABC):
    async def send_sms(self, phone: str, message: str, metadata: dict) -> SMSResult
    async def check_status(self, provider_message_id: str) -> SMSStatus
```

### 6. Payment Provider: Safaricom Daraja (M-Pesa)

**Decision**: Safaricom Daraja API for M-Pesa B2C payments

**Rationale**:
- **Market dominance**: M-Pesa is ubiquitous in Kenya (>90% mobile money market share)
- **Direct integration**: Better control and lower fees than aggregators
- **Sandbox available**: Comprehensive testing without real money
- **Well-documented**: Mature API with good developer resources

**Safety mechanisms**:
- `ENABLE_REAL_PAYMENTS=false` by default (must explicitly enable in production)
- `sandbox=true` flag required for all payment calls unless production mode
- Dual confirmation required for batch payments (API call + manual approval step)

## Product & Business Logic Decisions

### 7. Payment Calculation Formula

**Decision**: Configurable tiered pricing based on quality grade

**Formula** (default, configurable via env vars):
```
base_price_per_liter = Decimal(PRICE_PER_LITER)  # Default: 45.00 KES

quality_multiplier = {
    'A': 1.10,    # 10% premium
    'B': 1.00,    # Base price
    'C': 0.85,    # 15% penalty
    'Rejected': 0.00  # No payment
}

payment = quantity_liters * base_price_per_liter * quality_multiplier[grade]
```

**Configurable parameters**:
- `PRICE_PER_LITER`: Base price (KES)
- `QUALITY_GRADE_A_MULTIPLIER`: Default 1.10
- `QUALITY_GRADE_B_MULTIPLIER`: Default 1.00
- `QUALITY_GRADE_C_MULTIPLIER`: Default 0.85
- `MINIMUM_PAYMENT_THRESHOLD`: Minimum amount to trigger payout (default 100 KES)

**TODO for Product Owner**:
- [ ] Confirm exact pricing tiers and multipliers for pilot
- [ ] Determine if pricing varies by station/company
- [ ] Define handling of partial month payments (farmer leaves mid-month)
- [ ] Specify payment schedule (monthly on which date? End of month? 15th of next month?)

### 8. Offline Sync Conflict Resolution

**Decision**: Last-Write-Wins with manual override option

**Scenario**: Officer creates delivery offline, edits it offline, syncs. Meanwhile, same delivery was edited on server.

**Resolution strategy**:
1. **Deterministic IDs**: Client generates UUID v4 for deliveries when offline
2. **Conflict detection**: Compare `updated_at` timestamp - if server version is newer, flag as conflict
3. **Default behavior**: Server version wins (assumption: server edits are corrections by managers)
4. **Manual resolution**: Mobile app shows conflict UI with options:
   - Accept server version (discard local changes)
   - Accept local version (overwrite server)
   - Merge (for non-overlapping field changes)
5. **Audit**: All conflict resolutions logged to `audit_logs`

**Alternative considered**: Operational Transform (complex, overkill for this use case)

**TODO for Product Owner**:
- [ ] Confirm conflict resolution preference
- [ ] Define which fields are editable after initial creation (quantity? quality grade?)
- [ ] Specify time window for edits (e.g., deliveries only editable within 24 hours?)

### 9. Delivery Quantity Limits

**Decision**: Configurable per-delivery quantity limits

**Validation rules**:
- `MIN_DELIVERY_LITERS`: 0.1 (default)
- `MAX_DELIVERY_LITERS`: 200.0 (default)
- Validation error if outside range: 422 Unprocessable Entity

**Rationale**: Prevent data entry errors (e.g., typing 6800 instead of 6.8)

**TODO for Product Owner**:
- [ ] Confirm realistic min/max values for typical farmers
- [ ] Determine if limits vary by farmer (e.g., large commercial farms might exceed 200L)
- [ ] Specify behavior for exceptional cases (warning vs hard block)

### 10. SMS Character Limits & Encoding

**Decision**: SMS messages limited to 160 GSM characters (or 70 Unicode if Swahili characters present)

**Handling**:
- Template validation ensures messages stay within limits
- Long messages automatically split into multi-part SMS (with additional cost warning in logs)
- Use GSM 7-bit encoding where possible (cheaper than Unicode)

**Templates** (see app/services/sms_templates.py):

**English**:
```
Delivery: Dear {farmer_name}, you delivered {quantity}L on {date} to {station}. Thank you.
Monthly: Dear {farmer_name}, in {month} you delivered {total_liters}L. Est. payment: {amount} KES.
Rejected: Dear {farmer_name}, delivery on {date} was rejected. Reason: {reason}. Contact {station_contact}.
```

**Swahili** (TODO: Get proper translations):
```
Uwasilishaji: {farmer_name}, umetoa maziwa lita {quantity} tarehe {date} kwa {station}. Asante.
```

**TODO for Product Owner**:
- [ ] Provide approved Swahili SMS templates
- [ ] Confirm SMS sender ID (currently "DDCPTS" - may require carrier registration)
- [ ] Approve multi-part SMS cost (or enforce strict single-SMS limit)

### 11. Data Retention & Archival

**Decision**: Tiered retention with archival to S3

**Policy**:
- **Hot data** (PostgreSQL):
  - Current month deliveries: Full access
  - Last 12 months: Full access
  - >12 months: Archive to S3, remove from primary DB (keep summary records)
- **Audit logs**: 7 years retention (compliance assumption)
- **SMS logs**: 90 days hot, then archive
- **Backups**: 30 days daily backups, 12 monthly backups

**Archival process**:
- Monthly cron job moves old deliveries to S3 (Parquet format)
- Maintains `monthly_summaries` for reporting
- Archived data accessible via separate analytics endpoint (slower, S3-backed)

**TODO for Product Owner**:
- [ ] Confirm legal requirements for data retention (Kenya Data Protection Act compliance)
- [ ] Define archival timeline (12 months assumption - verify with legal/compliance)
- [ ] Specify PII deletion requirements (right to be forgotten requests)

### 12. Authentication & Security

**Decision**: JWT with refresh tokens, optional 2FA

**Flow**:
1. Login with email + password → returns access token (30 min) + refresh token (7 days)
2. Access token in Authorization header for API calls
3. Refresh token to get new access token when expired
4. Optional: OTP via SMS for 2FA (enabled per officer)

**Password policy**:
- Minimum 8 characters
- Must contain: uppercase, lowercase, number, special character
- Hashed with Argon2id (OWASP recommended, resistant to GPU attacks)
- No password reuse (last 5 passwords stored as hashes)

**Session management**:
- Refresh tokens stored in DB (can be revoked)
- Logout invalidates refresh token
- Admin can force-logout users (security incident response)

**TODO for Product Owner**:
- [ ] Confirm 2FA requirement (optional or mandatory for which roles?)
- [ ] Define password reset flow (SMS OTP? Email link? Security questions?)
- [ ] Specify session timeout for inactive users

### 13. Farmer Identification

**Decision**: Unique `farmer_code` as primary identifier, national ID optional

**Rationale**:
- Not all farmers have national IDs (especially older or marginalized communities)
- `farmer_code` is system-generated or farmer-chosen (e.g., "FARM-00123", "KIPKAREN-JOHN")
- Regex validation: `^[A-Z0-9\-\_]{3,32}$`
- Must be unique across the system

**National ID**:
- Optional field (nullable in DB)
- If provided, validated against Kenya ID format (8 digits)
- Used for KYC compliance in payment processing (M-Pesa may require it)

**TODO for Product Owner**:
- [ ] Confirm farmer_code generation strategy (auto-increment? station prefix + number?)
- [ ] Define process for farmers without national ID (alternative identification)
- [ ] Specify KYC requirements for M-Pesa payouts (Safaricom compliance)

### 14. Quality Grading Criteria

**Decision**: Four-tier grading system (A, B, C, Rejected)

**Criteria** (default, configurable):
- **Grade A**: Fat content ≥ 3.5%, no spoilage indicators
- **Grade B**: Fat content 3.0-3.4%, no spoilage
- **Grade C**: Fat content 2.5-2.9%, no spoilage
- **Rejected**: Fat content < 2.5% OR spoilage detected

**Measurement**:
- Fat content: Manual testing with lactometer (officer input) or automated sensor (future)
- Spoilage: Visual inspection + alcohol test (officer records yes/no)

**TODO for Product Owner**:
- [ ] Confirm exact fat content thresholds (dairy company standards)
- [ ] Define spoilage detection method and criteria
- [ ] Specify additional quality parameters (pH, antibiotics, adulterants)
- [ ] Determine if quality tests are mandatory or optional per delivery

### 15. Station & Company Structure

**Decision**: Multi-company support with station hierarchy

**Model**:
- Each `station` belongs to a `company` (e.g., "Brookside", "KCC")
- Officers assigned to one station
- Farmers registered at one primary station (can be changed)
- Deliveries always associated with station (for traceability)

**Rationale**: Kenya dairy market has multiple processors; system should support cooperative aggregation and multi-buyer scenarios

**TODO for Product Owner**:
- [ ] Confirm list of companies/processors for pilot
- [ ] Define farmer transfer process (changing primary station)
- [ ] Specify inter-station delivery rules (can farmer deliver to different station?)

### 16. Payment Batch Processing

**Decision**: Monthly batch payments with approval workflow

**Process**:
1. System generates monthly summaries (automated on 1st of each month)
2. Manager reviews summaries in dashboard
3. Manager initiates payment batch: `POST /api/v1/payments/disburse`
4. System creates payment records in `pending` status
5. Background job processes payments via M-Pesa B2C API
6. Status updates: `pending` → `sent` → `completed` (or `failed`)
7. SMS confirmation sent to farmers upon successful payment

**Approval workflow** (optional, configurable):
- `REQUIRE_PAYMENT_APPROVAL=true`: Manager creates batch, Admin approves
- `REQUIRE_PAYMENT_APPROVAL=false`: Manager directly initiates (default for pilot)

**Safety checks**:
- Dry-run mode: `POST /api/v1/payments/disburse?dry_run=true` (simulates, no actual payout)
- Total amount confirmation required (prevent fat-finger errors)
- Daily payment limit (configurable, default 1M KES)

**TODO for Product Owner**:
- [ ] Define approval workflow (single or dual approval?)
- [ ] Set payment limits (per farmer, per batch, per day)
- [ ] Specify payment failure handling (auto-retry? manual intervention? refund process?)

## Infrastructure Decisions

### 17. Hosting: AWS with managed services

**Decision**: AWS ECS Fargate + RDS + S3

**Architecture**:
- **Compute**: ECS Fargate (serverless containers, auto-scaling)
- **Database**: RDS PostgreSQL (Multi-AZ for production)
- **Storage**: S3 (backups, archived data, static assets)
- **Load balancing**: Application Load Balancer (ALB)
- **Networking**: VPC with public/private subnets
- **Secrets**: AWS Secrets Manager
- **Monitoring**: CloudWatch + Sentry + Prometheus

**Rationale**:
- **Managed services**: Reduce operational burden (no server patching)
- **Auto-scaling**: Handle traffic spikes during peak delivery times (morning)
- **Cost-effective**: Fargate cheaper than EC2 for variable workloads
- **Multi-region ready**: Easy to replicate to additional AWS regions if expanding beyond Kenya

**Alternative considered**: GCP GKE - also excellent, but AWS has better Terraform provider maturity

**TODO for DevOps/Infra**:
- [ ] Set up AWS organization and accounts (dev, staging, prod)
- [ ] Configure VPC peering for database access
- [ ] Implement auto-scaling policies (CPU/memory thresholds)
- [ ] Set up CloudWatch alarms for critical metrics

### 18. CI/CD: GitHub Actions

**Decision**: GitHub Actions for CI/CD pipeline

**Pipeline stages**:
1. **Lint & Typecheck** (on PR): Ruff, mypy, ESLint, Flutter analyze
2. **Unit Tests** (on PR): pytest, Jest, Flutter test
3. **Integration Tests** (on PR): Docker Compose + pytest
4. **Build** (on main merge): Docker images → push to ECR
5. **Deploy to Staging** (on main merge): Automatic
6. **Deploy to Production** (on tag): Manual approval required

**Rationale**:
- **GitHub-native**: No additional tooling, excellent integration
- **Free for open source / reasonable pricing for private repos
- **Matrix builds**: Test across Python versions, Node versions
- **Secrets management**: GitHub Secrets for credentials

**Alternative considered**: GitLab CI, CircleCI - both good but GitHub Actions has better ecosystem integration

## Open TODOs Requiring Product Owner Input

### Critical (Blocking MVP)
- [ ] **Pricing formula confirmation**: Exact price per liter and quality multipliers
- [ ] **Payment schedule**: Monthly payout date (1st? 15th? End of month?)
- [ ] **Farmer code format**: Auto-generated or manual? Prefix rules?
- [ ] **Quality grading thresholds**: Exact fat content % for grades A/B/C

### Important (Blocking Pilot)
- [ ] **Swahili SMS templates**: Translation and approval
- [ ] **Company/station list**: Pilot participants (Brookside? KCC? Cooperatives?)
- [ ] **Approval workflow**: Single or dual approval for payments?
- [ ] **National ID requirement**: Mandatory for payments? Alternative for farmers without ID?

### Nice-to-Have (Post-Pilot)
- [ ] **Data retention policy**: Legal requirements for PII and transaction data
- [ ] **Multi-language support**: Beyond English and Swahili
- [ ] **Custom quality parameters**: pH, antibiotics, other tests
- [ ] **Inter-station transfers**: Rules for farmer changing stations

## Assumptions Log

| Assumption | Rationale | Risk if Wrong | Mitigation |
|------------|-----------|---------------|------------|
| M-Pesa is preferred payment method | Market research shows 90%+ M-Pesa usage | Farmers prefer cash/bank | Implement payment method adapter (easy to add Airtel Money, bank transfer) |
| Officers have Android smartphones | Most affordable smartphones in Kenya are Android | Some officers have feature phones | Provide web-based alternative for delivery entry |
| SMS is reliable for confirmations | Ubiquitous in Kenya, works on all phones | SMS delivery failures | Implement retry logic, fallback to USSD, log all attempts |
| Monthly payments are acceptable | Industry standard for dairy cooperatives | Farmers need weekly payments | System design supports configurable payment frequency (trivial to change) |
| Internet connectivity at stations | Stations have at least intermittent 3G/4G | No connectivity | Offline-first mobile app handles this |
| PostgreSQL can handle scale | Proven at much larger scale than initial 10k deliveries/day | Unexpected bottlenecks | Design with sharding in mind, use connection pooling, monitor query performance |
| Farmers have M-Pesa accounts | Near-universal in Kenya | Some farmers don't | Provide agent cash pickup option (manual process) |

## References & Documentation

- **Africa's Talking SMS API**: https://developers.africastalking.com/docs/sms/overview
- **Safaricom Daraja API**: https://developer.safaricom.co.ke/Documentation
- **Kenya Data Protection Act**: https://www.odpc.go.ke/ (TODO: Legal review)
- **M-Pesa KYC Requirements**: https://www.safaricom.co.ke/mpesa_timeline/register-for-mpesa/

---

**Last Updated**: 2025-10-08  
**Review Frequency**: After each major feature completion or product owner feedback
