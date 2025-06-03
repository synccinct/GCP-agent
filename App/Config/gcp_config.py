"""Google Cloud Platform configuration and utilities."""

import os
import logging
from typing import Optional, Dict, Any
from google.cloud import secretmanager
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

class GCPConfig:
    """GCP configuration manager with credential handling."""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID")
        self.credentials = None
        self.secret_client = None
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID must be set")
        
        self._initialize_credentials()
        self._initialize_secret_manager()
    
    def _initialize_credentials(self):
        """Initialize GCP credentials."""
        try:
            self.credentials, _ = default()
            logger.info("GCP credentials initialized successfully")
        except DefaultCredentialsError as e:
            logger.error(f"Failed to initialize GCP credentials: {e}")
            raise
    
    def _initialize_secret_manager(self):
        """Initialize Secret Manager client."""
        try:
            self.secret_client = secretmanager.SecretManagerServiceClient(
                credentials=self.credentials
            )
            logger.info("Secret Manager client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Secret Manager: {e}")
            raise
    
    async def get_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """Retrieve secret from Secret Manager."""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            response = self.secret_client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            logger.debug(f"Retrieved secret: {secret_id}")
            return secret_value
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {e}")
            return None
    
    async def create_secret(self, secret_id: str, secret_value: str) -> bool:
        """Create a new secret in Secret Manager."""
        try:
            parent = f"projects/{self.project_id}"
            
            # Create the secret
            secret = {"replication": {"automatic": {}}}
            self.secret_client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret
                }
            )
            
            # Add the secret version
            self.secret_client.add_secret_version(
                request={
                    "parent": f"{parent}/secrets/{secret_id}",
                    "payload": {"data": secret_value.encode("UTF-8")}
                }
            )
            
            logger.info(f"Created secret: {secret_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create secret {secret_id}: {e}")
            return False
    
    async def update_secret(self, secret_id: str, secret_value: str) -> bool:
        """Update an existing secret in Secret Manager."""
        try:
            parent = f"projects/{self.project_id}/secrets/{secret_id}"
            
            # Add new version
            self.secret_client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": secret_value.encode("UTF-8")}
                }
            )
            
            logger.info(f"Updated secret: {secret_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update secret {secret_id}: {e}")
            return False
    
    def get_region_config(self) -> Dict[str, Any]:
        """Get region-specific configuration."""
        region = os.environ.get("GCP_REGION", "us-central1")
        zone = os.environ.get("GCP_ZONE", "us-central1-a")
        
        return {
            "region": region,
            "zone": zone,
            "firestore_location": self._get_firestore_location(region),
            "storage_location": self._get_storage_location(region),
        }
    
    def _get_firestore_location(self, region: str) -> str:
        """Get appropriate Firestore location for region."""
        region_mappings = {
            "us-central1": "us-central",
            "us-east1": "us-east1", 
            "us-west1": "us-west1",
            "europe-west1": "eur3",
            "asia-southeast1": "asia-southeast1",
        }
        return region_mappings.get(region, "us-central")
    
    def _get_storage_location(self, region: str) -> str:
        """Get appropriate Storage location for region."""
        if region.startswith("us-"):
            return "US"
        elif region.startswith("europe-"):
            return "EU"
        elif region.startswith("asia-"):
            return "ASIA"
        else:
            return "US"  # Default fallback
    
    def get_service_endpoints(self) -> Dict[str, str]:
        """Get GCP service endpoints."""
        return {
            "firestore": "firestore.googleapis.com",
            "storage": "storage.googleapis.com",
            "pubsub": "pubsub.googleapis.com",
            "secretmanager": "secretmanager.googleapis.com",
            "run": "run.googleapis.com",
            "cloudbuild": "cloudbuild.googleapis.com",
            "monitoring": "monitoring.googleapis.com",
            "logging": "logging.googleapis.com",
        }
    
    def validate_project_access(self) -> bool:
        """Validate access to GCP project."""
        try:
            # Try to list secrets as a basic access test
            parent = f"projects/{self.project_id}"
            list(self.secret_client.list_secrets(request={"parent": parent}))
            logger.info(f"Validated access to project: {self.project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to validate project access: {e}")
            return False

# Global GCP config instance
_gcp_config: Optional[GCPConfig] = None

def get_gcp_config() -> GCPConfig:
    """Get global GCP configuration instance."""
    global _gcp_config
    if _gcp_config is None:
        _gcp_config = GCPConfig()
    return _gcp_config

def initialize_gcp_config(project_id: str = None) -> GCPConfig:
    """Initialize GCP configuration."""
    global _gcp_config
    _gcp_config = GCPConfig(project_id)
    return _gcp_config
          
