# Third-Party Integration Notes

This document provides detailed integration steps for external services used by DDCPTS.

## Africa's Talking SMS Integration

### Setup Steps

1. **Create Account**
   - Sign up at https://account.africastalking.com/auth/register
   - Verify your email and phone number

2. **Get Sandbox Credentials**
   - Navigate to https://account.africastalking.com/apps/sandbox
   - Copy your Username (usually "sandbox")
   - Generate and copy API Key

3. **Configure Application**
   ```bash
   AFRICASTALKING_USERNAME=sandbox
   AFRICASTALKING_API_KEY=your-api-key-here
   AFRICASTALKING_SENDER_ID=DDCPTS
   ```

4. **Test SMS Sending**
   - Sandbox provides 100 free SMS per day
   - Test numbers must be added in sandbox dashboard
   - Format: +254XXXXXXXXX (Kenya)

5. **Production Migration**
   - Apply for production access
   - Purchase SMS credits
   - Register Sender ID (approval required, 1-2 weeks)
   - Update `AFRICASTALKING_ENVIRONMENT=production`

### Official Documentation
- API Docs: https://developers.africastalking.com/docs/sms/overview
- SMS Pricing: https://africastalking.com/pricing
- Sender ID Guide: https://help.africastalking.com/en/articles/3018799-how-to-register-a-sender-id

### Required Scopes/Permissions
- SMS Send permission (default in sandbox)

---

## Safaricom Daraja (M-Pesa) Integration

### Setup Steps

1. **Create Developer Account**
   - Register at https://developer.safaricom.co.ke/
   - Complete KYC verification

2. **Create Sandbox App**
   - Go to "My Apps" > "Add a new app"
   - Select APIs: "M-Pesa"
   - Note Consumer Key and Consumer Secret

3. **Configure Callback URLs**
   ```
   Queue Timeout URL: https://yourdomain.com/api/v1/mpesa/b2c/timeout
   Result URL: https://yourdomain.com/api/v1/mpesa/b2c/result
   ```

4. **Set Environment Variables**
   ```bash
   MPESA_ENVIRONMENT=sandbox
   MPESA_CONSUMER_KEY=your-consumer-key
   MPESA_CONSUMER_SECRET=your-consumer-secret
   MPESA_SHORTCODE=174379  # Sandbox default
   MPESA_PASSKEY=your-passkey
   MPESA_INITIATOR_NAME=testapi
   MPESA_INITIATOR_PASSWORD=Safaricom123!
   ```

5. **Test B2C Payment**
   - Use sandbox test numbers: 254708374149
   - Transactions are simulated (no real money)

6. **Production Setup** (Requires Business Approval)
   - Apply for production access (6-8 weeks approval)
   - Provide business documents (KRA PIN, certificate of incorporation)
   - Get production shortcode and security credentials
   - Set `MPESA_ENVIRONMENT=production`
   - **CRITICAL**: Set `ENABLE_REAL_PAYMENTS=true` ONLY after approval

### Official Documentation
- Developer Portal: https://developer.safaricom.co.ke/
- API Documentation: https://developer.safaricom.co.ke/APIs/MobileMoney
- Sandbox Guide: https://developer.safaricom.co.ke/sandbox-test
- Go-Live Checklist: https://developer.safaricom.co.ke/go-live

### Required Approvals
- Business registration verification
- M-Pesa Agent/Paybill application
- API access approval
- Production credentials (shortcode, initiator credentials)

### KYC Requirements for Payments
- National ID (for individuals)
- M-Pesa registered phone number
- Phone number format: 2547XXXXXXXX (no + prefix for API)

---

## Sentry Error Tracking

### Setup Steps

1. **Create Account**
   - Sign up at https://sentry.io/signup/

2. **Create Project**
   - Create a new Python project (for backend)
   - Create a new JavaScript project (for web)
   - Note the DSN for each

3. **Configure**
   ```bash
   SENTRY_DSN=https://xxx@sentry.io/xxx
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE_RATE=0.1
   ```

4. **Verify Integration**
   - Trigger a test error
   - Check Sentry dashboard for captured event

### Documentation
- Quick Start: https://docs.sentry.io/platforms/python/
- Performance Monitoring: https://docs.sentry.io/platforms/python/performance/

---

## AWS Deployment

### Prerequisites
- AWS Account with billing enabled
- IAM user with appropriate permissions
- AWS CLI configured locally

### Required AWS Services
- **ECR**: Container registry for Docker images
- **ECS**: Container orchestration (Fargate)
- **RDS**: PostgreSQL database
- **S3**: Backups and static files
- **CloudWatch**: Logging and monitoring
- **Secrets Manager**: Secure credential storage
- **VPC**: Network isolation

### Setup Steps

1. **Create S3 Bucket for Terraform State**
   ```bash
   aws s3 mb s3://ddcpts-terraform-state --region us-east-1
   aws s3api put-bucket-versioning \
     --bucket ddcpts-terraform-state \
     --versioning-configuration Status=Enabled
   ```

2. **Configure Terraform Backend**
   Edit `infra/terraform/main.tf` backend block

3. **Deploy Infrastructure**
   ```bash
   cd infra/terraform
   terraform init
   terraform plan -var-file=production.tfvars
   terraform apply -var-file=production.tfvars
   ```

4. **Push Docker Images to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t ddcpts-backend ./backend
   docker tag ddcpts-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ddcpts-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ddcpts-backend:latest
   ```

5. **Run Database Migrations**
   ```bash
   aws ecs execute-command \
     --cluster ddcpts-production \
     --task <task-id> \
     --command "alembic upgrade head" \
     --interactive
   ```

### Documentation
- ECS Best Practices: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/
- RDS Security: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.Security.html

---

## Security Checklist

### Before Production

- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Rotate all default passwords
- [ ] Enable 2FA for admin accounts
- [ ] Configure TLS/HTTPS (use AWS Certificate Manager)
- [ ] Set up WAF rules (SQL injection, XSS protection)
- [ ] Enable CloudWatch alarms for errors and resource limits
- [ ] Configure backup retention and test restore procedures
- [ ] Enable MFA for AWS root account
- [ ] Review IAM roles (least privilege principle)
- [ ] Set `ENABLE_REAL_PAYMENTS=false` until approved
- [ ] Conduct security audit/penetration testing

---

## Cost Optimization Tips

- Use AWS Free Tier where applicable (first 12 months)
- Start with t3.micro instances, scale up as needed
- Enable RDS instance auto-stop for non-production
- Use S3 lifecycle policies to archive old data to Glacier
- Set up billing alerts
- Use spot instances for non-critical tasks
- Right-size resources based on CloudWatch metrics

---

## Support & Troubleshooting

### Africa's Talking Support
- Email: support@africastalking.com
- Docs: https://help.africastalking.com/

### Safaricom Daraja Support
- Email: apisupport@safaricom.co.ke
- Developer Forum: https://developer.safaricom.co.ke/community

### AWS Support
- AWS Support Plans: https://aws.amazon.com/premiumsupport/plans/
- AWS Forums: https://repost.aws/
