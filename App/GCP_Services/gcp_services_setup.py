# GCP Services Setup and Configuration
import os
from google.cloud import firestore, storage, secretmanager
from google.cloud import run_v2
import subprocess

class GCPServicesSetup:
    """Setup and configure required GCP services"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.required_apis = [
            'run.googleapis.com',
            'cloudfunctions.googleapis.com',
            'firestore.googleapis.com',
            'secretmanager.googleapis.com',
            'cloudbuild.googleapis.com',
            'artifactregistry.googleapis.com'
        ]
    
    def enable_apis(self):
        """Enable required GCP APIs"""
        for api in self.required_apis:
            try:
                subprocess.run([
                    'gcloud', 'services', 'enable', api,
                    '--project', self.project_id
                ], check=True)
                print(f"Enabled API: {api}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to enable API {api}: {e}")
    
    def setup_firestore(self):
        """Initialize Firestore database"""
        db = firestore.Client(project=self.project_id)
        
        # Create initial collections
        collections = ['modules', 'applications', 'deployments']
        for collection in collections:
            doc_ref = db.collection(collection).document('_init')
            doc_ref.set({'created': firestore.SERVER_TIMESTAMP})
        
        print("Firestore initialized successfully")
    
    def setup_storage_buckets(self):
        """Create required storage buckets"""
        client = storage.Client(project=self.project_id)
        
        buckets = [
            f'{self.project_id}-module-artifacts',
            f'{self.project_id}-deployment-configs',
            f'{self.project_id}-static-assets'
        ]
        
        for bucket_name in buckets:
            try:
                bucket = client.bucket(bucket_name)
                bucket.create(location='US')
                print(f"Created bucket: {bucket_name}")
            except Exception as e:
                print(f"Bucket {bucket_name} may already exist: {e}")
    
    def setup_secrets(self):
        """Configure Secret Manager"""
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{self.project_id}"
        
        secrets = [
            'openai-api-key',
            'anthropic-api-key',
            'github-token'
        ]
        
        for secret_id in secrets:
            try:
                secret = {"replication": {"automatic": {}}}
                client.create_secret(
                    request={
                        "parent": parent,
                        "secret_id": secret_id,
                        "secret": secret
                    }
                )
                print(f"Created secret: {secret_id}")
            except Exception as e:
                print(f"Secret {secret_id} may already exist: {e}")

if __name__ == "__main__":
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        project_id = input("Enter your GCP project ID: ")
    
    setup = GCPServicesSetup(project_id)
    setup.enable_apis()
    setup.setup_firestore()
    setup.setup_storage_buckets()
    setup.setup_secrets()
      
