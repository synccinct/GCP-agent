# Microservice base class
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio

class MicroserviceBase(ABC):
    """Base class for all microservices"""
    
    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        self.dependencies: List[str] = []
        self.health_status = "healthy"
    
    @abstractmethod
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process service request"""
        pass
    
    @abstractmethod
    def get_api_spec(self) -> Dict[str, Any]:
        """Return OpenAPI specification"""
        pass
    
    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint"""
        return {
            "service": self.service_name,
            "version": self.version,
            "status": self.health_status,
            "timestamp": str(datetime.utcnow())
        }

# Frontend generator microservice
class FrontendGeneratorService(MicroserviceBase):
    """Microservice for generating frontend modules"""
    
    def __init__(self):
        super().__init__("frontend-generator", "1.0.0")
        self.dependencies = ["llm-service", "template-service"]
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate frontend module based on specifications"""
        
        framework = request.get("framework", "react")
        components = request.get("components", [])
        styling = request.get("styling", "tailwind")
        
        # Generate code using LLM
        generated_code = await self._generate_frontend_code(
            framework, components, styling
        )
        
        return {
            "module_type": "frontend",
            "framework": framework,
            "files": generated_code,
            "dependencies": self._get_npm_dependencies(framework),
            "build_config": self._get_build_config(framework)
        }
    
    def get_api_spec(self) -> Dict[str, Any]:
        """Return OpenAPI spec for frontend generator"""
        return {
            "openapi": "3.0.0",
            "info": {"title": "Frontend Generator", "version": "1.0.0"},
            "paths": {
                "/generate": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "framework": {"type": "string"},
                                            "components": {"type": "array"},
                                            "styling": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

# Backend generator microservice  
class BackendGeneratorService(MicroserviceBase):
    """Microservice for generating backend modules"""
    
    def __init__(self):
        super().__init__("backend-generator", "1.0.0")
        self.dependencies = ["llm-service", "database-service"]
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate backend module based on specifications"""
        
        language = request.get("language", "python")
        framework = request.get("framework", "fastapi")
        endpoints = request.get("endpoints", [])
        
        generated_code = await self._generate_backend_code(
            language, framework, endpoints
        )
        
        return {
            "module_type": "backend",
            "language": language,
            "framework": framework,
            "files": generated_code,
            "dependencies": self._get_package_dependencies(language),
            "deployment_config": self._get_deployment_config()
}
  
