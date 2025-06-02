# requirement_ingestion_flow.py
import time
import logging
from typing import Dict, Any
from .data_flow_manager import DataFlowEvent

class RequirementIngestionFlow:
    """Handles user requirements → Planning Agent → Module specifications"""
    
    def __init__(self, planning_agent, state_manager, event_publisher):
        self.planning_agent = planning_agent
        self.state_manager = state_manager
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)
    
    async def process_user_requirements(self, requirements: str, project_id: str) -> Dict[str, Any]:
        """Process user requirements through the ingestion flow"""
        
        flow_id = f"req_ingestion_{project_id}_{int(time.time())}"
        
        try:
            # Step 1: Validate and normalize requirements
            normalized_requirements = await self._normalize_requirements(requirements)
            
            # Step 2: Create initial application state
            app_state = await self.state_manager.create_application_state(
                project_id, 
                normalized_requirements
            )
            
            # Step 3: Send to Planning Agent
            planning_event = DataFlowEvent(
                event_id=f"planning_{int(time.time())}",
                event_type="requirements_to_planning",
                source_component="requirement_ingestion",
                target_component="planning_agent",
                payload={
                    "requirements": normalized_requirements,
                    "project_id": project_id,
                    "app_state_id": app_state["app_state_id"]
                },
                timestamp=time.time(),
                flow_id=flow_id,
                metadata={"priority": "high"}
            )
            
            await self.event_publisher.publish_event("planning_requests", planning_event)
            
            # Step 4: Wait for planning completion
            planning_result = await self._wait_for_planning_completion(flow_id)
            
            # Step 5: Update state with module specifications
            await self.state_manager.update_application_state(
                app_state["app_state_id"],
                {
                    "components": planning_result["module_specifications"],
                    "architecture": planning_result["architecture"],
                    "status": "planned"
                }
            )
            
            return {
                "flow_id": flow_id,
                "app_state_id": app_state["app_state_id"],
                "module_specifications": planning_result["module_specifications"],
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Requirement ingestion failed: {str(e)}")
            await self.event_publisher.publish_event("error_events", DataFlowEvent(
                event_id=f"error_{int(time.time())}",
                event_type="ingestion_error",
                source_component="requirement_ingestion",
                target_component="error_handler",
                payload={"error": str(e), "project_id": project_id},
                timestamp=time.time(),
                flow_id=flow_id,
                metadata={}
            ))
            
            return {
                "flow_id": flow_id,
                "success": False,
                "error": str(e)
            }
    
    async def _normalize_requirements(self, requirements: str) -> Dict[str, Any]:
        """Normalize and validate user requirements"""
        
        # Basic validation
        if not requirements or len(requirements.strip()) < 10:
            raise ValueError("Requirements too short or empty")
        
        # Extract structured information
        normalized = {
            "raw_requirements": requirements,
            "processed_at": time.time(),
            "word_count": len(requirements.split()),
            "complexity_estimate": self._estimate_complexity(requirements),
            "extracted_features": self._extract_features(requirements)
        }
        
        return normalized
    
    def _estimate_complexity(self, requirements: str) -> str:
        """Estimate complexity based on requirements text"""
        
        complexity_indicators = {
            "high": ["microservices", "real-time", "machine learning", "analytics", "enterprise"],
            "medium": ["authentication", "database", "api", "responsive", "mobile"],
            "low": ["simple", "basic", "static", "landing page"]
        }
        
        req_lower = requirements.lower()
        scores = {"high": 0, "medium": 0, "low": 0}
        
        for level, indicators in complexity_indicators.items():
            scores[level] = sum(1 for indicator in indicators if indicator in req_lower)
        
        return max(scores, key=scores.get)
    
    def _extract_features(self, requirements: str) -> Dict[str, Any]:
        """Extract features from requirements"""
        # Implementation for feature extraction
        return {"features": []}
    
    async def _wait_for_planning_completion(self, flow_id: str) -> Dict[str, Any]:
        """Wait for planning completion"""
        # Implementation for waiting for planning completion
        return {"module_specifications": [], "architecture": {}}
      
