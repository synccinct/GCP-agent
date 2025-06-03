output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "ai_agent_service_url" {
  description = "URL of the AI Agent Cloud Run service"
  value       = google_cloud_run_service.ai_agent.status[0].url
}

output "ai_agent_service_name" {
  description = "Name of the AI Agent Cloud Run service"
  value       = google_cloud_run_service.ai_agent.name
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository for container images"
  value       = google_artifact_registry_repository.ai_agent_repo.name
}

output "firestore_database" {
  description = "Firestore database name"
  value       = google_firestore_database.ai_agent_db.name
}

output "service_account_email" {
  description = "Email of the AI Agent service account"
  value       = google_service_account.ai_agent.email
}

output "secret_manager_secrets" {
  description = "List of created Secret Manager secrets"
  value = {
    openai_key    = google_secret_manager_secret.openai_key.secret_id
    anthropic_key = google_secret_manager_secret.anthropic_key.secret_id
  }
}

output "pubsub_topics" {
  description = "List of created Pub/Sub topics"
  value = {
    generation_events  = google_pubsub_topic.generation_events.name
    integration_events = google_pubsub_topic.integration_events.name
    deployment_events  = google_pubsub_topic.deployment_events.name
  }
}

output "pubsub_subscriptions" {
  description = "List of created Pub/Sub subscriptions"
  value = {
    generation_events_sub = google_pubsub_subscription.generation_events_sub.name
  }
}

output "monitoring_notification_channel" {
  description = "Monitoring notification channel"
  value       = google_monitoring_notification_channel.email.name
}

output "cloud_build_trigger" {
  description = "Cloud Build trigger for CI/CD"
  value       = google_cloudbuild_trigger.ai_agent_deploy.name
}

output "global_ip_address" {
  description = "Global IP address for load balancer"
  value       = google_compute_global_address.ai_agent_ip.address
}

output "ssl_certificate" {
  description = "Managed SSL certificate"
  value       = google_compute_managed_ssl_certificate.ai_agent_ssl.name
}

output "iam_roles" {
  description = "IAM roles assigned to service account"
  value = [
    "roles/firestore.user",
    "roles/secretmanager.secretAccessor",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/cloudbuild.builds.editor"
  ]
}

output "enabled_apis" {
  description = "List of enabled Google Cloud APIs"
  value = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "pubsub.googleapis.com"
  ]
}

output "deployment_commands" {
  description = "Commands to deploy the application"
  value = {
    docker_build = "docker build -t gcr.io/${var.project_id}/ai-agent:latest ."
    docker_push  = "docker push gcr.io/${var.project_id}/ai-agent:latest"
    cloud_build  = "gcloud builds submit --config cloudbuild.yaml"
    deploy_run   = "gcloud run deploy ai-agent-service --image gcr.io/${var.project_id}/ai-agent:latest --region ${var.region}"
  }
}

output "monitoring_dashboard_url" {
  description = "URL to access monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards?project=${var.project_id}"
}

output "logs_url" {
  description = "URL to access application logs"
  value       = "https://console.cloud.google.com/logs/query?project=${var.project_id}"
}

output "firestore_url" {
  description = "URL to access Firestore console"
  value       = "https://console.cloud.google.com/firestore?project=${var.project_id}"
}

output "cloud_run_url" {
  description = "URL to access Cloud Run console"
  value       = "https://console.cloud.google.com/run?project=${var.project_id}"
}

output "artifact_registry_url" {
  description = "URL to access Artifact Registry"
  value       = "https://console.cloud.google.com/artifacts?project=${var.project_id}"
}

output "secret_manager_url" {
  description = "URL to access Secret Manager"
  value       = "https://console.cloud.google.com/security/secret-manager?project=${var.project_id}"
}

output "pubsub_url" {
  description = "URL to access Pub/Sub console"
  value       = "https://console.cloud.google.com/cloudpubsub?project=${var.project_id}"
}

output "cloud_build_url" {
  description = "URL to access Cloud Build console"
  value       = "https://console.cloud.google.com/cloud-build?project=${var.project_id}"
}

output "setup_instructions" {
  description = "Setup instructions for the deployed infrastructure"
  value = <<-EOT
    1. Set up secrets in Secret Manager:
       - openai-api-key: Your OpenAI API key
       - anthropic-api-key: Your Anthropic API key
       
    2. Deploy the application:
       gcloud builds submit --config cloudbuild.yaml
       
    3. Access the application:
       ${google_cloud_run_service.ai_agent.status[0].url}
       
    4. Monitor the application:
       - Logs: ${google_cloud_run_service.ai_agent.status[0].url}/logs
       - Metrics: https://console.cloud.google.com/monitoring
       
    5. Configure DNS (if using custom domain):
       Point your domain to: ${google_compute_global_address.ai_agent_ip.address}
  EOT
}
