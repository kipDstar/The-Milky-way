variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ddcpts"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "ddcpts_prod"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "ddcpts_admin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "backend_image" {
  description = "Backend Docker image URI"
  type        = string
}

variable "web_image" {
  description = "Web Docker image URI"
  type        = string
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}
