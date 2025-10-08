# DDCPTS Admin Playbook

Operations guide for system administrators and managers.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monthly Payment Processing](#monthly-payment-processing)
3. [Backup & Restore](#backup--restore)
4. [Troubleshooting](#troubleshooting)
5. [Security Procedures](#security-procedures)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## Daily Operations

### Morning Checklist

1. **Check System Health**
   ```bash
   curl https://api.yourdomain.com/health
   ```
   Expected: `{"status": "healthy"}`

2. **Review Overnight Sync Status**
   - Check pending deliveries count
   - Review failed SMS logs
   - Verify database connection

3. **Monitor Key Metrics**
   - Today's deliveries count
   - SMS delivery success rate (target: >95%)
   - API response time (target: <500ms)

### End of Day Tasks

1. **Generate Daily Report**
   - Access: Web Dashboard > Reports > Daily
   - Download CSV for records
   - Review any anomalies (unusually high/low volumes)

2. **Check Failed Transactions**
   - Review SMS logs: `SELECT * FROM sms_logs WHERE status = 'failed'`
   - Retry failed SMS if needed
   - Document any persistent issues

---

## Monthly Payment Processing

### Pre-Payment Checks

1. **Generate Monthly Summaries** (1st of month)
   ```bash
   docker-compose exec backend python -m app.scripts.generate_monthly_summaries --month=2025-10
   ```

2. **Review Summaries**
   - Web Dashboard > Reports > Monthly
   - Check for anomalies (unusually high payments)
   - Verify farmer eligibility

3. **Run Dry-Run Payment**
   ```bash
   curl -X POST https://api.yourdomain.com/api/v1/payments/disburse \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"month": "2025-10", "dry_run": true, "sandbox": true}'
   ```

### Payment Execution

1. **Initiate Batch Payment**
   - Access: Web Dashboard > Payments > Disburse
   - Select month
   - **Verify total amount** before confirming
   - Click "Initiate Payment"

2. **Monitor Payment Status**
   ```sql
   SELECT status, COUNT(*) FROM payments 
   WHERE requested_at >= '2025-10-01' 
   GROUP BY status;
   ```

3. **Handle Failed Payments**
   - Identify failed payments
   - Verify farmer M-Pesa details
   - Retry manually or log for manual payout

### Post-Payment Tasks

1. **Send Monthly Summary SMS**
   - Automatic: System sends SMS after payment
   - Manual retry if needed

2. **Generate Payment Report**
   - Total disbursed amount
   - Success/failure rates
   - Farmers paid vs pending

3. **Archive Payment Records**
   ```bash
   docker-compose exec backend python -m app.scripts.archive_payments --month=2025-10
   ```

---

## Backup & Restore

### Daily Automated Backup

Backups run automatically at 2 AM via cron:

```bash
# View backup logs
docker-compose exec backend tail -f /var/log/backups.log

# List recent backups
aws s3 ls s3://ddcpts-backups/daily/
```

### Manual Backup

```bash
# Database backup
docker-compose exec db pg_dump -U ddcpts ddcpts_prod > backup_$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://ddcpts-backups/manual/
```

### Restore from Backup

**⚠️ WARNING: This will overwrite current data!**

1. **Stop application**
   ```bash
   docker-compose stop backend web
   ```

2. **Download backup**
   ```bash
   aws s3 cp s3://ddcpts-backups/daily/backup_20251008.sql ./restore.sql
   ```

3. **Restore database**
   ```bash
   docker-compose exec -T db psql -U ddcpts ddcpts_prod < restore.sql
   ```

4. **Verify data**
   ```sql
   SELECT COUNT(*) FROM deliveries;
   SELECT COUNT(*) FROM farmers;
   ```

5. **Restart application**
   ```bash
   docker-compose start backend web
   ```

### Backup Retention Policy

- **Daily backups**: 30 days
- **Monthly backups**: 12 months
- **Yearly archives**: 7 years (compliance)

---

## Troubleshooting

### SMS Not Sending

**Symptoms**: Farmers not receiving SMS confirmations

**Diagnosis**:
```sql
SELECT * FROM sms_logs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;
```

**Solutions**:
1. Check Africa's Talking balance/credits
2. Verify API key validity
3. Check phone number format (must be E.164: +254...)
4. Review provider response in `sms_logs.provider_response`

**Manual Retry**:
```bash
curl -X POST https://api.yourdomain.com/api/v1/sms/retry/<sms_log_id> \
  -H "Authorization: Bearer $TOKEN"
```

### Payment Failures

**Symptoms**: M-Pesa payments showing "failed" status

**Diagnosis**:
```sql
SELECT farmer_id, failure_reason, metadata 
FROM payments 
WHERE status = 'failed' 
ORDER BY requested_at DESC;
```

**Common Causes**:
- Insufficient balance in M-Pesa business account
- Invalid phone number
- Farmer account restrictions
- API timeout

**Solutions**:
1. Verify M-Pesa account balance
2. Confirm phone number format (254XXXXXXXXX, no +)
3. Check farmer M-Pesa registration status
4. Retry payment or arrange manual payout

### Database Connection Issues

**Symptoms**: "Database connection failed" errors

**Quick Fix**:
```bash
# Restart database
docker-compose restart db

# Check logs
docker-compose logs db

# Verify connection
docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

### Mobile App Sync Issues

**Symptoms**: Deliveries stuck in "pending" status

**Diagnosis**:
- Check mobile app connectivity
- Review API error logs
- Check for duplicate deliveries (client_generated_id conflicts)

**Solutions**:
1. Force sync from mobile app
2. Check server logs for errors
3. Verify delivery data format

---

## Security Procedures

### Password Reset (Officer/Manager)

1. **Admin Reset**:
   ```bash
   docker-compose exec backend python -m app.scripts.reset_password \
     --email=officer@example.com \
     --new-password="NewSecure@123"
   ```

2. **Force Password Change on Next Login**:
   ```sql
   UPDATE officers SET password_reset_required = TRUE WHERE email = 'officer@example.com';
   ```

### Key Rotation

**Rotate JWT Secret Key** (requires app restart):

1. Generate new key:
   ```bash
   openssl rand -hex 32
   ```

2. Update `.env`:
   ```
   SECRET_KEY=<new-key>
   ```

3. Restart:
   ```bash
   docker-compose restart backend
   ```

⚠️ **Note**: All users will be logged out

**Rotate M-Pesa Credentials**:

1. Get new credentials from Daraja portal
2. Update `.env`:
   ```
   MPESA_CONSUMER_KEY=<new-key>
   MPESA_CONSUMER_SECRET=<new-secret>
   ```
3. Restart backend

### Audit Log Review

**Weekly Security Audit**:
```sql
SELECT entity_type, action, COUNT(*) as count
FROM audit_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY entity_type, action
ORDER BY count DESC;
```

**Suspicious Activity**:
```sql
SELECT * FROM audit_logs
WHERE action IN ('deleted', 'updated')
  AND entity_type = 'payment'
  AND timestamp >= NOW() - INTERVAL '1 day';
```

### Incident Response

1. **Detect**: Monitor alerts, user reports
2. **Contain**: Disable affected accounts, block IPs
3. **Investigate**: Review audit logs, database changes
4. **Recover**: Restore from backup if needed
5. **Document**: Record incident in incident log
6. **Prevent**: Update security measures

---

## Monitoring & Alerts

### Key Metrics to Monitor

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| API Response Time | >1s | Warning |
| API Response Time | >3s | Critical |
| SMS Delivery Rate | <90% | Warning |
| SMS Delivery Rate | <80% | Critical |
| Database CPU | >70% | Warning |
| Database CPU | >90% | Critical |
| Payment Failure Rate | >10% | Warning |
| Disk Usage | >80% | Warning |

### Alert Channels

- **Email**: critical-alerts@yourdomain.com
- **SMS**: +254712XXXXXX (on-call admin)
- **Slack**: #ddcpts-alerts

### Dashboard Access

- **Sentry**: https://sentry.io/organizations/yourorg/issues/
- **CloudWatch**: AWS Console > CloudWatch > Dashboards
- **Grafana**: http://monitoring.yourdomain.com (if deployed)

### Common Alerts

**High Error Rate**:
- Check Sentry for exceptions
- Review application logs
- Verify external service status (M-Pesa, Africa's Talking)

**Database Connection Spike**:
- Check for slow queries
- Review connection pool settings
- Consider scaling RDS instance

**Disk Space Low**:
- Clean up old logs: `docker system prune`
- Archive old deliveries
- Increase volume size if needed

---

## Scaling Procedures

### Horizontal Scaling (More Instances)

**ECS Auto-scaling**:
```bash
aws ecs update-service \
  --cluster ddcpts-production \
  --service backend \
  --desired-count 4
```

### Vertical Scaling (Bigger Instances)

**Database**:
```bash
aws rds modify-db-instance \
  --db-instance-identifier ddcpts-production \
  --db-instance-class db.t3.medium \
  --apply-immediately
```

### Load Testing

Before scaling:
```bash
# Install k6
brew install k6

# Run load test
k6 run load-test.js
```

---

## Maintenance Windows

### Planned Maintenance

1. **Schedule** (off-peak hours): 2 AM - 4 AM EAT
2. **Notify users**: Email + SMS 48 hours in advance
3. **Backup**: Take full backup before changes
4. **Execute**: Run updates/migrations
5. **Test**: Verify functionality
6. **Monitor**: Watch for issues post-deployment

### Emergency Maintenance

1. **Assess impact**
2. **Notify stakeholders immediately**
3. **Execute fix**
4. **Communicate resolution**

---

## Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| System Admin | admin@yourdomain.com | Infrastructure, deployments |
| Database Admin | dba@yourdomain.com | Database performance, backups |
| On-Call Engineer | +254712XXXXXX | After-hours critical issues |
| Product Owner | po@yourdomain.com | Business decisions |

---

## Quick Reference Commands

```bash
# Check system status
docker-compose ps

# View logs
docker-compose logs -f backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python -m app.scripts.create_admin

# Generate monthly summaries
docker-compose exec backend python -m app.scripts.generate_summaries

# Database backup
docker-compose exec db pg_dump -U ddcpts ddcpts_prod > backup.sql

# Restart services
docker-compose restart backend web

# Scale services
docker-compose up -d --scale backend=3
```

---

**Last Updated**: 2025-10-08  
**Version**: 1.0
