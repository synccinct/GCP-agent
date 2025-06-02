# code_generation_flow.py
import time
import logging
from typing import Dict, List, Any
from .data_flow_manager import DataFlowEvent

class CodeGenerationFlow:
    """Handles Module specifications → Module Generator → Code artifacts"""
    
    def __init__(self, module_generators, state_manager, event_publisher):
        self.module_generators = module_generators
        self.state_manager = state_manager
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)
        self.active_generations: Dict[str, Dict] = {}
    
    async def process_module_specifications(self, app_state_id: str, specifications: List[Dict]) -> Dict[str, Any]:
        """Process module specifications through code generation flow"""
        
        flow_id = f"code_gen_{app_state_id}_{int(time.time())}"
        
        try:
            # Step 1: Validate specifications
            validated_specs = await self._validate_specifications(specifications)
            
            # Step 2: Determine generation order based on dependencies
            generation_order = self._calculate_generation_order(validated_specs)
            
            # Step 3: Generate modules in dependency order
            generation_results = {}
            
            for spec in generation_order:
                generation_event = DataFlowEvent(
                    event_id=f"gen_{spec['id']}_{int(time.time())}",
                    event_type="specification_to_generator",
                    source_component="code_generation_flow",
                    target_component=f"{spec['type']}_generator",
                    payload={
                        "specification": spec,
                        "app_state_id": app_state_id,
                        "dependencies": spec.get("dependencies", [])
                    },
                    timestamp=time.time(),
                    flow_id=flow_id,
                    metadata={"generation_order": generation_order.index(spec)}
                )
                
                await self.event_publisher.publish_event("generation_requests", generation_event)
                
                # Wait for generation completion
                generation_result = await self._wait_for_generation_completion(
                    spec['id'], 
                    flow_id
                )
                
                generation_results[spec['id']] = generation_result
                
                # Update state with generated artifacts
                await self.state_manager.update_component_state(
                    app_state_id,
                    spec['id'],
                    {
                        "status": "complete" if generation_result["success"] else "error",
                        "artifacts": generation_result.get("artifacts", []),
                        "generated_at": time.time()
                    }
                )
                
                # If generation failed, handle error
                if not generation_result["success"]:
                    await self._handle_generation_error(spec, generation_result, flow_id)
                    break
            
            # Step 4: Validate all generations completed successfully
            success = all(result["success"] for result in generation_results.values())
            
            return {
                "flow_id": flow_id,
                "app_state_id": app_state_id,
                "generation_results": generation_results,
                "success": success
            }
            
        except Exception as e:
            self.logger.error(f"Code generation flow failed: {str(e)}")
            return {
                "flow_id": flow_id,
                "success": False,
                "error": str(e)
            }
    
    def _calculate_generation_order(self, specifications: List[Dict]) -> List[Dict]:
        """Calculate optimal generation order based on dependencies"""
        
        # Create dependency graph
        spec_map = {spec['id']: spec for spec in specifications}
        ordered_specs = []
        processed = set()
        
        def can_process(spec):
            dependencies = spec.get("dependencies", [])
            return all(dep in processed for dep in dependencies)
        
        while len(processed) < len(specifications):
            # Find specs that can be processed (all dependencies met)
            ready_specs = [
                spec for spec in specifications 
                if spec['id'] not in processed and can_process(spec)
            ]
            
            if not ready_specs:
                # Circular dependency or missing dependency
                remaining = [spec for spec in specifications if spec['id'] not in processed]
                self.logger.warning(f"Potential circular dependency detected: {[s['id'] for s in remaining]}")
                # Process remaining specs anyway
                ready_specs = remaining
            
            # Sort by priority (database first, then backend, then frontend)
            priority_order = {"database": 0, "auth": 1, "backend": 2, "frontend": 3}
            ready_specs.sort(key=lambda x: priority_order.get(x.get("type", "unknown"), 99))
            
            for spec in ready_specs:
                ordered_specs.append(spec)
                processed.add(spec['id'])
        
        return ordered_specs
    
    async def _validate_specifications(self, specifications: List[Dict]) -> List[Dict]:
        """Validate specifications"""
        # Implementation for validation
        return specifications
    
    async def _wait_for_generation_completion(self, spec_id: str, flow_id: str) -> Dict[str, Any]:
        """Wait for generation completion"""
        # Implementation for waiting
        return {"success": True, "artifacts": []}
    
    async def _handle_generation_error(self, spec: Dict, result: Dict, flow_id: str):
        """Handle generation error"""
        # Implementation for error handling
        pass
      
