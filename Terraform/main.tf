terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "pubsub.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "ai_agent_repo" {
  location      = var.region
  repository_id = "ai-agent-images"
  description   = "Container images for AI Agent system"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run service for AI Agent
resource "google_cloud_run_service" "ai_agent" {
  name     = "ai-agent-service"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-agent-images/ai-agent:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.openai_key.secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
      }
      
      service_account_name = google_service_account.ai_agent.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.required_apis]
}

# Service account for AI Agent
resource "google_service_account" "ai_agent" {
  account_id   = "ai-agent-service"
  display_name = "AI Agent Service Account"
  description  = "Service account for AI Agent application"
}

# IAM bindings for service account
resource "google_project_iam_member" "ai_agent_permissions" {
  for_each = toset([
    "roles/firestore.user",
    "roles/secretmanager.secretAccessor",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/cloudbuild.builds.editor"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ai_agent.email}"
}

# Firestore database
resource "google_firestore_database" "ai_agent_db" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_region
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.required_apis]
}

# Secret Manager secrets
resource "google_secret_manager_secret" "openai_key" {
  secret_id = "openai-api-key"
  
  replication {
    automatic = true
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "anthropic_key" {
  secret_id = "anthropic-api-key"
  
  replication {
    automatic = true
  }
  
  depends_on = [google_project_service.required_apis]
}

# Pub/Sub topics for event-driven architecture
resource "google_pubsub_topic" "generation_events" {
  name = "generation-events"
  
  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "integration_events" {
  name = "integration-events"
  
  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "deployment_events" {
  name = "deployment-events"
  
  depends_on = [google_project_service.required_apis]
}

# Pub/Sub subscriptions
resource "google_pubsub_subscription" "generation_events_sub" {
  name  = "generation-events-subscription"
  topic = google_pubsub_topic.generation_events.name
  
  ack_deadline_seconds = 20
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Cloud Build trigger for CI/CD
resource "google_cloudbuild_trigger" "ai_agent_deploy" {
  name        = "ai-agent-deploy"
  description = "Deploy AI Agent on code changes"
  
  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }
  
  filename = "cloudbuild.yaml"
  
  depends_on = [google_project_service.required_apis]
}

# Monitoring alert policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "AI Agent High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  depends_on = [google_project_service.required_apis]
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notifications"
  type         = "email"
  
  labels = {
    email_address = var.notification_email
  }
}

# Load balancer for high availability
resource "google_compute_global_address" "ai_agent_ip" {
  name = "ai-agent-global-ip"
}

resource "google_compute_managed_ssl_certificate" "ai_agent_ssl" {
  name = "ai-agent-ssl-cert"
  
  managed {
    domains = [var.domain_name]
  }
}
