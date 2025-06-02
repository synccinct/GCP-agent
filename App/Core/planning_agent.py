# planning_agent.py
import asyncio
import json
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
    
    def _load_planning_templates(self) -> Dict[str, str]:
        """Load planning prompt templates"""
        return {
            "requirement_extraction": """
            Extract structured requirements from: {user_input}
            Focus on: functionality, data needs, user types, performance, security
            """,
            "architecture_analysis": """
            Analyze application requirements and recommend:
            - Architecture patterns
            - Technology stack
            - Deployment strategy
            - Scalability approach
            """,
            "component_breakdown": """
            Break down application into components:
            - Frontend requirements
            - Backend services
            - Data storage needs
            - Authentication requirements
            - Integration points
            """
        }
    
    def _load_architecture_patterns(self) -> Dict[str, Dict]:
        """Load predefined architecture patterns"""
        return {
            "simple_web_app": {
                "components": ["frontend", "backend", "database"],
                "patterns": ["mvc", "rest_api"],
                "deployment": "cloud_run",
                "complexity": "low"
            },
            "microservices_app": {
                "components": ["frontend", "api_gateway", "services", "database", "auth"],
                "patterns": ["microservices", "event_driven", "cqrs"],
                "deployment": "gke",
                "complexity": "high"
            },
            "serverless_app": {
                "components": ["frontend", "functions", "database", "auth"],
                "patterns": ["serverless", "event_driven"],
                "deployment": "cloud_functions",
                "complexity": "medium"
            }
        }

class TaskExecutionEngine:
    """Execute planned tasks with monitoring and error handling"""
    
    def __init__(self, llm_manager, performance_monitor):
        self.llm_manager = llm_manager
        self.performance_monitor = performance_monitor
        self.active_tasks: Dict[str, Dict] = {}
        self.task_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
    
    async def execute_architecture_plan(self, architecture: ApplicationArchitecture) -> Dict[str, Any]:
        """Execute the complete architecture plan"""
        
        execution_result = {
            "app_id": architecture.app_id,
            "status": "in_progress",
            "start_time": time.time(),
            "component_results": {},
            "integration_result": None,
            "deployment_result": None,
            "errors": [],
            "metrics": {}
        }
        
        try:
            # Step 1: Execute component generation in dependency order
            sorted_components = self._sort_components_by_dependency(architecture.components)
            
            for component in sorted_components:
                component_result = await self._execute_component_generation(component)
                execution_result["component_results"][component.component_id] = component_result
                
                if not component_result["success"]:
                    execution_result["errors"].append(f"Component {component.component_id} failed")
            
            # Step 2: Execute integration if all components succeeded
            if all(result["success"] for result in execution_result["component_results"].values()):
                integration_result = await self._execute_integration(architecture, execution_result["component_results"])
                execution_result["integration_result"] = integration_result
                
                # Step 3: Execute deployment if integration succeeded
                if integration_result["success"]:
                    deployment_result = await self._execute_deployment(architecture, integration_result)
                    execution_result["deployment_result"] = deployment_result
                    
                    execution_result["status"] = "completed" if deployment_result["success"] else "failed"
                else:
                    execution_result["status"] = "failed"
                    execution_result["errors"].append("Integration failed")
            else:
                execution_result["status"] = "failed"
                execution_result["errors"].append("Component generation failed")
            
            # Record execution metrics
            execution_time = time.time() - execution_result["start_time"]
            execution_result["metrics"]["total_execution_time"] = execution_time
            
            self.performance_monitor.record_metric(
                "application_generation_time",
                execution_time,
                "seconds",
                {
                    "component_count": len(architecture.components),
                    "complexity": architecture.components[0].estimated_complexity if architecture.components else "medium"
                }
            )
            
        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["errors"].append(str(e))
            self.logger.error(f"Architecture execution failed: {str(e)}")
        
        return execution_result
    
    async def _execute_component_generation(self, component: ComponentSpec) -> Dict[str, Any]:
        """Execute generation of a single component"""
        
        start_time = time.time()
        
        try:
            # Create generation request based on component type
            if component.component_type == "frontend":
                result = await self._generate_frontend_component(component)
            elif component.component_type == "backend":
                result = await self._generate_backend_component(component)
            elif component.component_type == "database":
                result = await self._generate_database_component(component)
            elif component.component_type == "auth":
                result = await self._generate_auth_component(component)
            else:
                raise ValueError(f"Unknown component type: {component.component_type}")
            
            generation_time = time.time() - start_time
            
            self.performance_monitor.record_metric(
                "module_generation_time",
                generation_time,
                "seconds",
                {
                    "module_type": component.component_type,
                    "framework": component.framework,
                    "complexity": component.estimated_complexity
                }
            )
            
            return {
                "success": True,
                "component_id": component.component_id,
                "generation_time": generation_time,
                "files": result.get("files", {}),
                "dependencies": result.get("dependencies", []),
                "config": result.get("config", {})
            }
            
        except Exception as e:
            self.logger.error(f"Component generation failed for {component.component_id}: {str(e)}")
            return {
                "success": False,
                "component_id": component.component_id,
                "error": str(e),
                "generation_time": time.time() - start_time
            }
    
    async def _generate_frontend_component(self, component: ComponentSpec) -> Dict[str, Any]:
        """Generate frontend component using LLM"""
        
      
