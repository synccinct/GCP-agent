import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = Field(default="AI Agent GCP Generator", env="APP_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # GCP Configuration
    gcp_project_id: str = Field(..., env="GCP_PROJECT_ID")
    gcp_region: str = Field(default="us-central1", env="GCP_REGION")
    gcp_zone: str = Field(default="us-central1-a", env="GCP_ZONE")
    
    # LLM Provider Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_ai_api_key: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")
    
    # Database Configuration
    firestore_database: str = Field(default="(default)", env="FIRESTORE_DATABASE")
    
    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Performance Settings
    max_concurrent_generations: int = Field(default=10, env="MAX_CONCURRENT_GENERATIONS")
    generation_timeout_seconds: int = Field(default=300, env="GENERATION_TIMEOUT_SECONDS")
    
    # Storage
    artifact_storage_bucket: str = Field(..., env="ARTIFACT_STORAGE_BUCKET")
    template_storage_bucket: str = Field(..., env="TEMPLATE_STORAGE_BUCKET")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=100, env="RATE_LIMIT_RPM")
    rate_limit_tokens_per_minute: int = Field(default=100000, env="RATE_LIMIT_TPM")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
