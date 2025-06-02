# Backend for Frontend pattern
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import httpx

class BFFService:
    """Backend for Frontend service"""
    
    def __init__(self, service_name: str):
        self.app = FastAPI(title=f"{service_name} BFF")
        self.service_registry = {}
        self.setup_routes()
    
    def setup_routes(self):
        """Setup BFF routes"""
        
        @self.app.get("/api/dashboard")
        async def get_dashboard_data():
            """Aggregate data for dashboard frontend"""
            
            # Fetch data from multiple microservices
            tasks = [
                self._fetch_modules_data(),
                self._fetch_deployments_data(),
                self._fetch_metrics_data()
            ]
            
            modules, deployments, metrics = await asyncio.gather(*tasks)
            
            # Transform data for frontend consumption
            dashboard_data = {
                "modules": self._transform_modules_for_dashboard(modules),
                "deployments": self._transform_deployments_for_dashboard(deployments),
                "metrics": self._transform_metrics_for_dashboard(metrics),
                "summary": self._generate_summary(modules, deployments, metrics)
            }
            
            return dashboard_data
        
        @self.app.get("/api/module-builder")
        async def get_module_builder_data():
            """Aggregate data for module builder frontend"""
            
            # Fetch different data set for module builder
            tasks = [
                self._fetch_templates_data(),
                self._fetch_frameworks_data(),
                self._fetch_integration_options()
            ]
            
            templates, frameworks, integrations = await asyncio.gather(*tasks)
            
            return {
                "templates": templates,
                "frameworks": frameworks,
                "integration_options": integrations,
                "recommendations": self._get_recommendations()
            }
    
    async def _fetch_modules_data(self) -> List[Dict[str, Any]]:
        """Fetch modules data from module service"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.service_registry['module-service']}/modules"
            )
            return response.json()
    
    def _transform_modules_for_dashboard(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform modules data for dashboard consumption"""
        
        return [
            {
                "id": module["id"],
                "name": module["name"],
                "type": module["type"],
                "status": module["status"],
                "last_updated": module["updated_at"],
                "health_score": self._calculate_health_score(module)
            }
            for module in modules
        ]

# Mobile BFF service
class MobileBFFService(BFFService):
    """BFF specifically for mobile applications"""
    
    def __init__(self):
        super().__init__("Mobile")
    
    def setup_routes(self):
        """Setup mobile-specific routes"""
        
        @self.app.get("/api/mobile/modules")
        async def get_mobile_modules():
            """Get modules data optimized for mobile"""
            
            modules = await self._fetch_modules_data()
            
            # Return minimal data for mobile bandwidth optimization
            return [
                {
                    "id": module["id"],
                    "name": module["name"],
                    "type": module["type"],
                    "status": module["status"]
                }
                for module in modules
            ]
        
        @self.app.post("/api/mobile/quick-generate")
        async def quick_generate_module(request: Dict[str, Any]):
            """Quick module generation for mobile"""
            
            # Simplified generation for mobile use case
            result = await self._generate_module_mobile_optimized(request)
            return {"module_id": result["id"], "status": "generating"}

# Web BFF service
class WebBFFService(BFFService):
    """BFF specifically for web applications"""
    
    def __init__(self):
        super().__init__("Web")
    
    def setup_routes(self):
        """Setup web-specific routes"""
        
        @self.app.get("/api/web/modules/detailed")
        async def get_detailed_modules():
            """Get detailed modules data for web interface"""
            
            modules = await self._fetch_modules_data()
            
            # Enrich with additional data for web interface
            detailed_modules = []
            for module in modules:
                detailed_module = module.copy()
                detailed_module["code_preview"] = await self._get_code_preview(module["id"])
                detailed_module["dependencies"] = await self._get_dependencies(module["id"])
                detailed_module["metrics"] = await self._get_module_metrics(module["id"])
                detailed_modules.append(detailed_module)
            
            return detailed_modules
      
