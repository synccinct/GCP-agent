import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass

@dataclass
class CompatibilityIssue:
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "api", "data", "dependency", "security"
    description: str
    affected_modules: List[str]
    suggested_fix: str
    auto_fixable: bool

class CompatibilityChecker:
    """Advanced compatibility checking with contextual error recovery"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)
        self.compatibility_rules = self._load_compatibility_rules()
    
    async def check_module_compatibility(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive compatibility analysis with contextual awareness"""
        
        compatibility_result = {
            "overall_compatible": True,
            "compatibility_score": 0.0,
            "issues": [],
            "recommendations": [],
            "auto_fixes_available": [],
            "integration_complexity": "low"
        }
        
        try:
            # API compatibility check
            api_issues = await self._check_api_compatibility(modules)
            compatibility_result["issues"].extend(api_issues)
            
            # Data model compatibility
            data_issues = await self._check_data_compatibility(modules)
            compatibility_result["issues"].extend(data_issues)
            
            # Dependency compatibility
            dependency_issues = await self._check_dependency_compatibility(modules)
            compatibility_result["issues"].extend(dependency_issues)
            
            # Security compatibility
            security_issues = await self._check_security_compatibility(modules)
            compatibility_result["issues"].extend(security_issues)
            
            # Performance compatibility
            performance_issues = await self._check_performance_compatibility(modules)
            compatibility_result["issues"].extend(performance_issues)
            
            # Calculate overall compatibility
            compatibility_result = await self._calculate_compatibility_metrics(compatibility_result)
            
            # Generate contextual recommendations
            compatibility_result["recommendations"] = await self._generate_contextual_recommendations(
                modules, compatibility_result["issues"]
            )
            
            # Identify auto-fixable issues
            compatibility_result["auto_fixes_available"] = [
                issue for issue in compatibility_result["issues"] if issue.auto_fixable
            ]
            
        except Exception as e:
            self.logger.error(f"Compatibility check failed: {str(e)}")
            compatibility_result["error"] = str(e)
        
        return compatibility_result
    
    async def _check_api_compatibility(self, modules: List[Dict[str, Any]]) -> List[CompatibilityIssue]:
        """Check API contract compatibility between modules"""
        
        issues = []
        api_contracts = {}
        
        # Extract API contracts from each module
        for module in modules:
            if module.get("module_type") in ["frontend", "backend"]:
                contract = await self._extract_api_contract(module)
                api_contracts[module["id"]] = contract
        
        # Check contract compatibility
        for producer_id, producer_contract in api_contracts.items():
            for consumer_id, consumer_contract in api_contracts.items():
                if producer_id != consumer_id:
                    contract_issues = await self._compare_api_contracts(
                        producer_contract, consumer_contract, producer_id, consumer_id
                    )
                    issues.extend(contract_issues)
        
        return issues
    
    async def _extract_api_contract(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API contract from module using LLM analysis"""
        
        module_code = module.get("files", {})
        specifications = module.get("specifications", {})
        
        extraction_prompt = f"""
        Analyze this module and extract its API contract:
        
        Module Type: {module.get("module_type")}
        Framework: {module.get("framework")}
        Specifications: {json.dumps(specifications, indent=2)}
        
        Extract:
        1. Exposed endpoints (if backend)
        2. Expected API calls (if frontend)
        3. Data models and schemas
        4. Authentication requirements
        5. Error response formats
        
        Return as JSON with clear structure.
        """
        
        from app.llm_integration.llm_manager import LLMRequest
        
        request = LLMRequest(
            prompt=extraction_prompt,
            model="gpt-4o",
            max_tokens=2000,
            temperature=0.1,
            system_message="You are an API contract analyzer. Extract precise API specifications."
        )
        
        response = await self.llm_manager.generate(request)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"endpoints": [], "data_models": [], "auth_requirements": []}
    
    def _load_compatibility_rules(self) -> Dict[str, Any]:
        """Load compatibility rules"""
        return {
            "framework_compatibility": {
                "react": ["express", "fastapi", "firestore", "firebase_auth"],
                "vue": ["express", "fastapi", "firestore", "firebase_auth"],
                "angular": ["express", "fastapi", "cloud_sql", "firebase_auth"]
            },
            "database_compatibility": {
                "firestore": ["fastapi", "express", "firebase_auth"],
                "cloud_sql": ["fastapi", "express", "custom_auth"]
            }
      }
          
