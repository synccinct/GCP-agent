variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone for resources"
  type        = string
  default     = "us-central1-a"
}

variable "firestore_region" {
  description = "The region for Firestore database"
  type        = string
  default     = "us-central"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = ""
}

variable "notification_email" {
  description = "Email for monitoring notifications"
  type        = string
}

variable "domain_name" {
  description = "Domain name for SSL certificate"
  type        = string
  default     = ""
}

variable "ai_agent_image" {
  description = "Container image for AI Agent"
  type        = string
  default     = "gcr.io/PROJECT_ID/ai-agent:latest"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "CPU limit for Cloud Run instances"
  type        = string
  default     = "2"
}

variable "memory_limit" {
  description = "Memory limit for Cloud Run instances"
  type        = string
  default     = "4Gi"
}

variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable structured logging"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_schedule" {
  description = "Cron schedule for backups"
  type        = string
  default     = "0 2 * * *"  # Daily at 2 AM
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default = {
    project     = "ai-agent"
    environment = "dev"
    managed-by  = "terraform"
  }
}

variable "firestore_backup_retention" {
  description = "Firestore backup retention in days"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

variable "monitoring_retention_days" {
  description = "Monitoring data retention in days"
  type        = number
  default     = 90
}

variable "enable_vpc" {
  description = "Enable custom VPC network"
  type        = bool
  default     = false
}

variable "vpc_cidr" {
  description = "CIDR block for VPC network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "enable_nat" {
  description = "Enable Cloud NAT for private instances"
  type        = bool
  default     = false
}

variable "enable_ssl" {
  description = "Enable SSL certificate"
  type        = bool
  default     = false
}

variable "ssl_domains" {
  description = "Domains for SSL certificate"
  type        = list(string)
  default     = []
}

variable "cors_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "rate_limit_rpm" {
  description = "Rate limit requests per minute"
  type        = number
  default     = 100
}

variable "enable_cdn" {
  description = "Enable Cloud CDN"
  type        = bool
  default     = false
}

variable "enable_armor" {
  description = "Enable Cloud Armor security policies"
  type        = bool
  default     = false
}

variable "secret_names" {
  description = "List of secrets to create in Secret Manager"
  type        = list(string)
  default = [
    "openai-api-key",
    "anthropic-api-key",
    "jwt-secret-key",
    "github-token"
  ]
}

variable "pubsub_topics" {
  description = "List of Pub/Sub topics to create"
  type        = list(string)
  default = [
    "generation-events",
    "integration-events",
    "deployment-events",
    "error-events"
  ]
}

variable "firestore_collections" {
  description = "List of Firestore collections to initialize"
  type        = list(string)
  default = [
    "application_states",
    "task_status",
    "user_sessions",
    "performance_metrics",
    "error_logs"
  ]
}

variable "enable_workload_identity" {
  description = "Enable Workload Identity for GKE"
  type        = bool
  default     = false
}

variable "gke_node_count" {
  description = "Number of GKE nodes"
  type        = number
  default     = 3
}

variable "gke_machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-4"
}

variable "enable_preemptible" {
  description = "Use preemptible instances for cost savings"
  type        = bool
  default     = false
}

variable "disk_size_gb" {
  description = "Disk size in GB for instances"
  type        = number
  default     = 100
}

variable "disk_type" {
  description = "Disk type for instances"
  type        = string
  default     = "pd-standard"
}
