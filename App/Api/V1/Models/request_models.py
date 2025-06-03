from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ArchitectureRequest(BaseModel):
    """Request model for architecture generation"""
    project_id: str = Field(..., description="Unique project identifier")
    requirements: str = Field(..., min_length=10, description="Natural language requirements")
    context: Dict[str, Any] = Field(default={}, description="Additional context")

class GenerationRequest(BaseModel):
    """Request model for complete application generation"""
    project_id: str = Field(..., description="Unique project identifier")
    requirements: str = Field(..., min_length=10, description="Natural language requirements")
    name: str = Field(..., description="Application name")
    priority: int = Field(default=5, ge=1, le=10, description="Generation priority")

class ModuleRequest(BaseModel):
    """Request model for individual module generation"""
    module_type: str = Field(..., regex="^(frontend|backend|database|auth)$")
    framework: str = Field(..., description="Framework to use")
    specifications: Dict[str, Any] = Field(..., description="Module specifications")
    dependencies: List[str] = Field(default=[], description="Module dependencies")

class IntegrationRequest(BaseModel):
    """Request model for module integration"""
    project_id: str = Field(..., description="Project identifier")
    modules: List[str] = Field(..., description="Module IDs to integrate")
    integration_type: str = Field(default="full_stack", description="Integration pattern")
    target_platform: str = Field(default="gcp", description="Target deployment platform")

class DeploymentRequest(BaseModel):
    """Request model for application deployment"""
    project_id: str = Field(..., description="Project identifier")
    deployment_target: str = Field(default="cloud_run", description="Deployment target")
    configuration: Dict[str, Any] = Field(default={}, description="Deployment configuration")
  
