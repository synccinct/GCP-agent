from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional
import asyncio
import json
import time
import logging

from app.api.v1.models.request_models import (
    GenerationRequest, ModuleRequest, ArchitectureRequest
)
from app.api.v1.models.response_models import (
    GenerationResponse, ModuleResponse, ArchitectureResponse, StatusResponse
)
from app.core.planning_agent import PlanningAgent
from app.core.task_execution_engine import TaskExecutionEngine
from app.api.v1.middleware.authentication import get_current_user
from app.api.v1.middleware.rate_limiting import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/architecture", response_model=ArchitectureResponse)
async def generate_architecture(
    request: ArchitectureRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(rate_limit(requests_per_minute=10))
):
    """Generate application architecture from requirements with contextual error recovery"""
    
    try:
        # Get planning agent from app state
        from app.main import planning_agent, performance_monitor
        
        if not planning_agent:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Planning agent not available"
            )
        
        # Start performance monitoring
        operation_id = f"arch_gen_{request.project_id}_{int(time.time())}"
        performance_monitor.start_operation_trace(
            operation_id, "architecture_generation", 
            {"user_id": current_user["user_id"], "project_id": request.project_id}
        )
        
        # Generate architecture with circuit breaker protection
        try:
            architecture = await planning_agent.analyze_requirements(
                request.requirements, request.project_id
            )
        except Exception as e:
            # Attempt contextual recovery
            recovery_result = await _attempt_architecture_recovery(request, e)
            if recovery_result["success"]:
                architecture = recovery_result["architecture"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Architecture generation failed: {recovery_result['error']}"
                )
        
        # End performance monitoring
        performance_monitor.end_operation_trace(operation_id, True, {"architecture": architecture.__dict__})
        
        return ArchitectureResponse(
            success=True,
            architecture_id=architecture.app_id,
            components=[comp.__dict__ for comp in architecture.components],
            integration_patterns=architecture.integration_patterns,
            deployment_strategy=architecture.deployment_strategy,
            gcp_services=architecture.gcp_services,
            estimated_timeline=architecture.estimated_timeline
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Architecture generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Architecture generation failed: {str(e)}"
        )

@router.post("/generate/application", response_model=GenerationResponse)
async def generate_application(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(rate_limit(requests_per_minute=5))
):
    """Generate complete application from requirements with self-healing capabilities"""
    
    try:
        from app.main import planning_agent, execution_engine, state_manager
        
        # Start background task for application generation
        task_id = f"app_gen_{request.project_id}_{int(time.time())}"
        
        background_tasks.add_task(
            _generate_application_background,
            task_id, request, current_user["user_id"]
        )
        
        return GenerationResponse(
            success=True,
            task_id=task_id,
            status="started",
            message="Application generation started in background with self-healing enabled"
        )
        
    except Exception as e:
        logger.error(f"Application generation request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/generate/status/{task_id}", response_model=StatusResponse)
async def get_generation_status(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get status of application generation task with real-time updates"""
    
    try:
        from app.main import state_manager
        
        # Get task status from state manager
        task_status = await state_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return StatusResponse(
            task_id=task_id,
            status=task_status["status"],
            progress=task_status.get("progress", 0),
            current_step=task_status.get("current_step", ""),
            estimated_completion=task_status.get("estimated_completion"),
            results=task_status.get("results", {}),
            errors=task_status.get("errors", []),
            recovery_actions=task_status.get("recovery_actions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/generate/stream/{task_id}")
async def stream_generation_progress(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Stream real-time generation progress with error recovery updates"""
    
    async def generate_progress_stream():
        """Generate Server-Sent Events for real-time updates"""
        
        try:
            from app.main import state_manager
            
            while True:
                task_status = await state_manager.get_task_status(task_id)
                
                if not task_status:
                    yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                    break
                
                # Send status update with recovery information
                status_data = {
                    "task_id": task_id,
                    "status": task_status["status"],
                    "progress": task_status.get("progress", 0),
                    "current_step": task_status.get("current_step", ""),
                    "timestamp": time.time(),
                    "recovery_actions": task_status.get("recovery_actions", []),
                    "self_healing_active": task_status.get("self_healing_active", False)
                }
                
                yield f"data: {json.dumps(status_data)}\n\n"
                
                # Break if task is complete or failed
                if task_status["status"] in ["completed", "failed"]:
                    break
                
                # Wait before next update
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Stream generation failed: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

async def _generate_application_background(task_id: str, request: GenerationRequest, user_id: str):
    """Background task for application generation with self-healing"""
    
    try:
        from app.main import planning_agent, execution_engine, state_manager, error_framework
        
        # Update task status
        await state_manager.update_task_status(task_id, {
            "status": "planning",
            "progress": 10,
            "current_step": "Analyzing requirements",
            "self_healing_active": True
        })
        
        # Generate architecture with error recovery
        try:
            architecture = await planning_agent.analyze_requirements(
                request.requirements, request.project_id
            )
        except Exception as e:
            # Attempt self-healing recovery
            recovery_result = await error_framework.recover_from_error(e, {
                "operation_id": task_id,
                "component": "planning_agent",
                "user_id": user_id,
                "project_id": request.project_id,
                "request_data": request.dict(),
                "system_state": {},
                "previous_attempts": []
            })
            
            if recovery_result["success"]:
                architecture = recovery_result["final_result"]
                await state_manager.update_task_status(task_id, {
                    "recovery_actions": recovery_result["recovery_actions_taken"]
                })
            else:
                await state_manager.update_task_status(task_id, {
                    "status": "failed",
                    "progress": 0,
                    "current_step": "Planning failed",
                    "errors": [str(e)],
                    "recovery_actions": recovery_result["recovery_actions_taken"]
                })
                return
        
        await state_manager.update_task_status(task_id, {
            "status": "generating",
            "progress": 30,
            "current_step": "Generating modules"
        })
        
        # Execute application generation with self-healing
        execution_result = await execution_engine.execute_architecture_plan(architecture)
        
        if execution_result["success"]:
            await state_manager.update_task_status(task_id, {
                "status": "completed",
                "progress": 100,
                "current_step": "Generation complete",
                "results": execution_result
            })
        else:
            await state_manager.update_task_status(task_id, {
                "status": "failed",
                "progress": 0,
                "current_step": "Generation failed",
                "errors": execution_result.get("errors", [])
            })
            
    except Exception as e:
        logger.error(f"Background generation failed: {str(e)}")
        await state_manager.update_task_status(task_id, {
            "status": "failed",
            "progress": 0,
            "current_step": "Generation failed",
            "errors": [str(e)]
        })

async def _attempt_architecture_recovery(request: ArchitectureRequest, error: Exception) -> Dict[str, Any]:
    """Attempt contextual recovery for architecture generation failures"""
    
    try:
        from app.main import llm_manager
        
        # Simplify requirements for retry
        simplified_requirements = await _simplify_requirements(request.requirements)
        
        # Retry with simplified requirements
        from app.main import planning_agent
        architecture = await planning_agent.analyze_requirements(
            simplified_requirements, request.project_id
        )
        
        return {
            "success": True,
            "architecture": architecture,
            "recovery_method": "requirements_simplification"
        }
        
    except Exception as recovery_error:
        return {
            "success": False,
            "error": str(recovery_error),
            "recovery_method": "failed"
        }

async def _simplify_requirements(requirements: str) -> str:
    """Simplify complex requirements for recovery"""
    
    # Basic simplification - in production this would use LLM
    simplified = requirements.replace("advanced", "basic")
    simplified = simplified.replace("complex", "simple")
    simplified = simplified.replace("enterprise", "standard")
    
    return simplified
                      
