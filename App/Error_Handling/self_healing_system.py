import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import traceback

class HealingStrategy(Enum):
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK_TO_TEMPLATE = "fallback_to_template"
    REDUCE_COMPLEXITY = "reduce_complexity"
    ALTERNATIVE_PROVIDER = "alternative_provider"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"

@dataclass
class ErrorPattern:
    pattern_id: str
    error_signature: str
    frequency: int
    success_rate_with_strategy: Dict[HealingStrategy, float]
    context_factors: List[str]

class SelfHealingSystem:
    """Self-healing AI system with predictive maintenance and continuous learning"""
    
    def __init__(self, llm_manager, state_manager, performance_monitor):
        self.llm_manager = llm_manager
        self.state_manager = state_manager
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(__name__)
        
        # Circuit breaker states for different components
        self.circuit_breakers = {}
        
        # Error pattern learning
        self.error_patterns: Dict[str, ErrorPattern] = {}
        
        # Predictive maintenance thresholds
        self.maintenance_thresholds = {
            "error_rate": 0.1,  # 10% error rate triggers maintenance
            "latency_increase": 2.0,  # 2x latency increase
            "memory_usage": 0.9  # 90% memory usage
        }
    
    async def heal_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main self-healing entry point with predictive capabilities"""
        
        healing_result = {
            "success": False,
            "healing_strategy_used": None,
            "healing_actions": [],
            "predictive_actions": [],
            "learning_updates": [],
            "requires_human_intervention": False
        }
        
        try:
            # Detect error patterns and predict future failures
            error_signature = self._generate_error_signature(error, context)
            pattern_analysis = await self._analyze_error_patterns(error_signature, context)
            
            # Predictive maintenance check
            predictive_actions = await self._perform_predictive_maintenance(context)
            healing_result["predictive_actions"] = predictive_actions
            
            # Select healing strategy based on learned patterns
            healing_strategy = await self._select_healing_strategy(
                error, context, pattern_analysis
            )
            
            if healing_strategy:
                # Execute healing with circuit breaker protection
                component_id = context.get("component", "unknown")
                
                if await self._check_circuit_breaker(component_id):
                    healing_execution = await self._execute_healing_strategy(
                        healing_strategy, error, context
                    )
                    
                    healing_result.update(healing_execution)
                    
                    # Update circuit breaker based on result
                    await self._update_circuit_breaker(component_id, healing_result["success"])
                else:
                    healing_result["healing_actions"].append("Circuit breaker OPEN - healing blocked")
                    healing_result["requires_human_intervention"] = True
            
            # Continuous learning update
            learning_update = await self._update_learning_models(
                error_signature, healing_strategy, healing_result, context
            )
            healing_result["learning_updates"] = learning_update
            
        except Exception as healing_error:
            self.logger.error(f"Self-healing process failed: {str(healing_error)}")
            healing_result["healing_actions"].append(f"Healing process failed: {str(healing_error)}")
        
        return healing_result
    
    def _generate_error_signature(self, error: Exception, context: Dict[str, Any]) -> str:
        """Generate unique signature for error pattern recognition"""
        
        error_type = type(error).__name__
        error_message_hash = hash(str(error)[:100])  # First 100 chars
        component = context.get("component", "unknown")
        
        return f"{error_type}_{component}_{error_message_hash}"
              
