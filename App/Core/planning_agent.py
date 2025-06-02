# planning_agent.py
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class ComponentSpec:
    """Specification for a component to be generated"""
    component_id: str
    component_type: str  # frontend, backend, database, auth
    framework: str
    specifications: Dict[str, Any]
    dependencies: List[str]
    priority: int
    estimated_complexity: str  # low, medium, high

@dataclass
class ApplicationArchitecture:
    """Complete application architecture definition"""
    app_id: str
    app_name: str
    description: str
    components: List[ComponentSpec]
    integration_patterns: List[str]
    deployment_strategy: str
    gcp_services: List[str]
    estimated_timeline: int  # minutes

class PlanningAgent:
    """Orchestrates the overall application generation process"""
    
    def __init__(self, llm_manager, performance_monitor):
        self.llm_manager = llm_manager
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(__name__)
        self.planning_templates = self._load_planning_templates()
        self.architecture_patterns = self._load_architecture_patterns()
    
    async def analyze_requirements(self, user_requirements: str) -> ApplicationArchitecture:
        """Analyze user requirements and create application architecture"""
        
        start_time = time.time()
        
        try:
            # Step 1: Extract structured requirements using LLM
            structured_requirements = await self._extract_structured_requirements(user_requirements)
            
            # Step 2: Determine application type and complexity
            app_analysis = await self._analyze_application_type(structured_requirements)
            
            # Step 3: Select appropriate architecture pattern
            architecture_pattern = self._select_architecture_pattern(app_analysis)
            
            # Step 4: Generate component specifications
            components = await self._generate_component_specs(structured_requirements, architecture_pattern)
            
            # Step 5: Determine integration patterns
            integration_patterns = self._determine_integration_patterns(components)
            
            # Step 6: Select GCP services
            gcp_services = self._select_gcp_services(components, app_analysis)
            
            # Step 7: Estimate timeline
            timeline = self._estimate_timeline(components)
            
            architecture = ApplicationArchitecture(
                app_id=f"app_{int(time.time())}",
                app_name=structured_requirements.get("app_name", "Generated App"),
                description=structured_requirements.get("description", ""),
                components=components,
                integration_patterns=integration_patterns,
                deployment_strategy=app_analysis.get("deployment_strategy", "cloud_run"),
                gcp_services=gcp_services,
                estimated_timeline=timeline
            )
            
            # Record performance metrics
            planning_time = time.time() - start_time
            self.performance_monitor.record_metric(
                "planning_time", 
                planning_time, 
                "seconds",
                {"complexity": app_analysis.get("complexity", "medium")}
            )
            
            self.logger.info(f"Architecture planning completed in {planning_time:.2f}s")
            return architecture
            
        except Exception as e:
            self.logger.error(f"Planning failed: {str(e)}")
            raise
    
    async def _extract_structured_requirements(self, user_requirements: str) -> Dict[str, Any]:
        """Extract structured requirements from natural language"""
        
        extraction_prompt = f"""
        Analyze the following user requirements and extract structured information:
        
        Requirements: {user_requirements}
        
        Extract and return a JSON object with:
        - app_name: string
        - description: string
        - app_type: string (web_app, api, dashboard, e_commerce, etc.)
        - features: array of strings
        - user_types: array of strings
        - data_requirements: object
        - performance_requirements: object
        - security_requirements: object
        - integration_requirements: array
        
        Respond with valid JSON only.
        """
        
        from llm_manager import LLMRequest  # Import here to avoid circular imports
        
        request = LLMRequest(
            prompt=extraction_prompt,
            model="gpt-4o",
            max_tokens=1500,
            temperature=0.3,
            system_message="You are an expert software architect. Extract structured requirements from user descriptions."
        )
        
        response = await self.llm_manager.generate(request)
        
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            # Fallback to basic extraction
            return {
                "app_name": "Generated Application",
                "description": user_requirements,
                "app_type": "web_app",
                "features": ["basic_functionality"],
                "user_types": ["end_user"],
                "data_requirements": {},
                "performance_requirements": {},
                "security_requirements": {},
                "integration_requirements": []
            }
    
    async def _analyze_application_type(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze application type and complexity"""
        
        analysis_prompt = f"""
        Analyze this application specification and determine:
        
        Requirements: {json.dumps(requirements, indent=2)}
        
        Provide analysis as JSON:
        {{
            "complexity": "low|medium|high|very_high",
            "deployment_strategy": "cloud_run|app_engine|gke|hybrid",
            "scalability_needs": "low|medium|high",
            "data_complexity": "simple|moderate|complex",
            "integration_complexity": "minimal|moderate|extensive",
            "security_level": "basic|standard|high|enterprise",
            "recommended_patterns": ["pattern1", "pattern2"]
        }}
        """
        
        from llm_manager import LLMRequest
        
        request = LLMRequest(
            prompt=analysis_prompt,
            model="gpt-4o",
            max_tokens=800,
            temperature=0.2
        )
        
        response = await self.llm_manager.generate(request)
        
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {
                "complexity": "medium",
                "deployment_strategy": "cloud_run",
                "scalability_needs": "medium",
                "data_complexity": "moderate",
                "integration_complexity": "moderate",
                "security_level": "standard",
                "recommended_patterns": ["microservices", "event_driven"]
            }
    
    def _select_architecture_pattern(self, app_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate architecture pattern based on analysis"""
        complexity = app_analysis.get("complexity", "medium")
        
        if complexity in ["low"]:
            return self.architecture_patterns["simple_web_app"]
        elif complexity in ["high", "very_high"]:
            return self.architecture_patterns["microservices_app"]
        else:
            return self.architecture_patterns["serverless_app"]
    
    async def _generate_component_specs(self, requirements: Dict[str, Any], pattern: Dict[str, Any]) -> List[ComponentSpec]:
        """Generate detailed component specifications"""
        
        components = []
        component_id_counter = 1
        
        # Frontend component
        if requirements.get("app_type") in ["web_app", "dashboard", "e_commerce"]:
            frontend_spec = ComponentSpec(
                component_id=f"frontend_{component_id_counter}",
                component_type="frontend",
                framework=self._select_frontend_framework(requirements),
                specifications={
                    "features": requirements.get("features", []),
                    "user_types": requirements.get("user_types", []),
                    "ui_complexity": pattern.get("complexity", "medium"),
                    "responsive": True,
                    "pwa": requirements.get("pwa_required", False)
                },
                dependencies=[],
                priority=1,
                estimated_complexity=pattern.get("complexity", "medium")
            )
            components.append(frontend_spec)
            component_id_counter += 1
        
        # Backend component
        backend_spec = ComponentSpec(
            component_id=f"backend_{component_id_counter}",
            component_type="backend",
            framework=self._select_backend_framework(requirements, pattern),
            specifications={
                "api_type": "rest",
                "endpoints": self._generate_endpoint_specs(requirements),
                "business_logic": requirements.get("features", []),
                "scalability": pattern.get("scalability_needs", "medium"),
                "async_processing": pattern.get("integration_complexity") == "extensive"
            },
            dependencies=[],
            priority=2,
            estimated_complexity=pattern.get("complexity", "medium")
        )
        components.append(backend_spec)
        component_id_counter += 1
        
        # Database component
        if requirements.get("data_requirements") or pattern.get("data_complexity") != "simple":
            database_spec = ComponentSpec(
                component_id=f"database_{component_id_counter}",
                component_type="database",
                framework=self._select_database_type(requirements, pattern),
                specifications={
                    "data_models": self._extract_data_models(requirements),
                    "relationships": self._determine_relationships(requirements),
                    "scalability": pattern.get("scalability_needs", "medium"),
                    "consistency": "strong" if pattern.get("data_complexity") == "complex" else "eventual"
                },
                dependencies=[],
                priority=3,
                estimated_complexity=pattern.get("data_complexity", "moderate")
            )
            components.append(database_spec)
            component_id_counter += 1
        
        # Authentication component
        if pattern.get("security_level") in ["standard", "high", "enterprise"]:
            auth_spec = ComponentSpec(
                component_id=f"auth_{component_id_counter}",
                component_type="auth",
                framework=self._select_auth_framework(pattern),
                specifications={
                    "auth_methods": self._determine_auth_methods(requirements, pattern),
                    "user_management": True,
                    "role_based_access": pattern.get("security_level") in ["high", "enterprise"],
                    "multi_factor": pattern.get("security_level") == "enterprise",
                    "social_login": "social_auth" in requirements.get("features", [])
                },
                dependencies=[],
                priority=4,
                estimated_complexity="medium"
            )
            components.append(auth_spec)
        
        # Set dependencies
        self._set_component_dependencies(components)
        
        return components
    
    def _select_frontend_framework(self, requirements: Dict[str, Any]) -> str:
        """Select appropriate frontend framework"""
        
        app_type = requirements.get("app_type", "web_app")
        complexity = len(requirements.get("features", []))
        
        if app_type == "dashboard" or complexity > 10:
            return "react"
        elif app_type == "e_commerce":
            return "next.js"
        elif complexity < 5:
            return "vanilla_js"
        else:
            return "react"
    
    def _select_backend_framework(self, requirements: Dict[str, Any], pattern: Dict[str, Any]) -> str:
        """Select appropriate backend framework"""
        
        complexity = pattern.get("complexity", "medium")
        scalability = pattern.get("scalability_needs", "medium")
        
        if complexity == "high" or scalability == "high":
            return "fastapi"
        elif pattern.get("deployment_strategy") == "cloud_run":
            return "express"
        else:
            return "fastapi"
    
    def _select_database_type(self, requirements: Dict[str, Any], pattern: Dict[str, Any]) -> str:
        """Select appropriate database type"""
        data_complexity = pattern.get("data_complexity", "moderate")
        
        if data_complexity == "complex":
            return "postgresql"
        elif data_complexity == "simple":
            return "firestore"
        else:
            return "postgresql"
    
    def _select_auth_framework(self, pattern: Dict[str, Any]) -> str:
        """Select appropriate authentication framework"""
        security_level = pattern.get("security_level", "standard")
        
        if security_level in ["high", "enterprise"]:
            return "firebase_auth"
        else:
            return "jwt"
    
    def _generate_endpoint_specs(self, requirements: Dict[str, Any]) -> List[str]:
        """Generate
            
