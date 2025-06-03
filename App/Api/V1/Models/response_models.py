from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ArchitectureResponse(BaseModel):
    """Response model for architecture generation"""
    success: bool
    architecture_id: str
    components: List[Dict[str, Any]]
    integration_patterns: List[str]
    deployment_strategy: str
    gcp_services: List[str]
    estimated_timeline: int

class GenerationResponse(BaseModel):
    """Response model for application generation"""
    success: bool
    task_id: str
    status: str
    message: str

class ModuleResponse(BaseModel):
    """Response model for module generation"""
    success: bool
    module_id: str
    artifacts: List[str] = Field(default=[], description="Generated file paths")
    dependencies: List[str] = Field(default=[], description="Required dependencies")
    generation_time: float = Field(description="Generation time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error details if failed")

class IntegrationResponse(BaseModel):
    """Response model for integration"""
    success: bool
    integration_id: str
    integrated_artifacts: List[str] = Field(default=[], description="Integration artifacts")
    compatibility_score: float = Field(ge=0.0, le=1.0, description="Module compatibility score")
    issues: List[str] = Field(default=[], description="Integration issues found")

class StatusResponse(BaseModel):
    """Response model for status queries"""
    task_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    current_step: str
    estimated_completion: Optional[float] = None
    results: Dict[str, Any] = Field(default={})
    errors: List[str] = Field(default=[])
    recovery_actions: List[str] = Field(default=[])

class DeploymentResponse(BaseModel):
    """Response model for deployment"""
    success: bool
    deployment_id: str
    service_urls: Dict[str, str] = Field(default={})
    deployment_status: str
    logs: List[str] = Field(default=[])
  
