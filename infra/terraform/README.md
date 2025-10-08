# DDCPTS Terraform Infrastructure

This directory contains Terraform configurations for deploying DDCPTS to AWS.

## Architecture

- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **ECS Fargate**: Containerized application deployment
- **RDS PostgreSQL**: Managed database (Multi-AZ for production)
- **S3**: Backups and archived data storage
- **ALB**: Application Load Balancer for traffic distribution
- **CloudWatch**: Monitoring and logging
- **Secrets Manager**: Secure credential storage

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- S3 bucket for Terraform state (create manually)

## Deployment Steps

### 1. Initialize Terraform

```bash
terraform init
```

### 2. Create Variables File

Create `terraform.tfvars`:

```hcl
environment = "production"
db_password = "your-secure-password"
secret_key  = "your-secret-key"
backend_image = "123456789.dkr.ecr.us-east-1.amazonaws.com/ddcpts-backend:latest"
web_image = "123456789.dkr.ecr.us-east-1.amazonaws.com/ddcpts-web:latest"
```

### 3. Plan Deployment

```bash
terraform plan -var-file=terraform.tfvars
```

### 4. Deploy Infrastructure

```bash
terraform apply -var-file=terraform.tfvars
```

### 5. Run Database Migrations

```bash
# Connect to ECS task and run migrations
aws ecs execute-command \
  --cluster ddcpts-production \
  --task <task-id> \
  --command "alembic upgrade head" \
  --interactive
```

## Environments

- **Development**: `development.tfvars`
- **Staging**: `staging.tfvars`
- **Production**: `production.tfvars`

## Estimated Costs (Monthly)

- ECS Fargate (2 tasks): ~$30
- RDS PostgreSQL (db.t3.micro): ~$15
- ALB: ~$18
- S3 Storage: ~$5
- **Total**: ~$70/month (can scale up/down)

## Security Considerations

- Database in private subnet (no public access)
- Secrets stored in AWS Secrets Manager
- TLS encryption in transit
- Encryption at rest for RDS and S3
- Security groups restrict network access
- IAM roles follow least privilege

## Backup & Disaster Recovery

- RDS automated backups (35 days retention)
- Daily backups to S3
- Point-in-time recovery enabled
- Multi-AZ deployment for high availability

## Monitoring

- CloudWatch Logs for application logs
- CloudWatch Metrics for resource monitoring
- Alarms for critical metrics (CPU, memory, errors)
- SNS topics for notifications

## Cleanup

```bash
terraform destroy -var-file=terraform.tfvars
```

**Warning**: This will permanently delete all resources!
