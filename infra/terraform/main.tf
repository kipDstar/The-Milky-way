# DDCPTS Terraform Infrastructure Configuration
# AWS ECS Fargate + RDS PostgreSQL + S3

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configure S3 backend for state management
    # bucket  = "ddcpts-terraform-state"
    # key     = "production/terraform.tfstate"
    # region  = "us-east-1"
    # encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# RDS PostgreSQL Database
module "database" {
  source = "./modules/database"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  db_instance_class   = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
}

# ECS Cluster and Services
module "ecs" {
  source = "./modules/ecs"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  
  backend_image      = var.backend_image
  web_image          = var.web_image
  
  database_url       = module.database.connection_string
  secret_key         = var.secret_key
}

# S3 Buckets for backups and archives
module "storage" {
  source = "./modules/storage"
  
  project_name = var.project_name
  environment  = var.environment
}

# Outputs
output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "s3_backup_bucket" {
  description = "S3 bucket for database backups"
  value       = module.storage.backup_bucket_name
}
