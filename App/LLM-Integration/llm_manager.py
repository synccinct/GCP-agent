"""Multi-provider manager with failover and load balancing"""

import time
import logging
import backoff
from typing import Dict, List, Any, Optional

from .base import LLMProvider, GenerationRequest

class LLMManager:
    """Manage multiple LLM providers with failover and load balancing"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.provider_priority: List[str] = []
        self.health_status: Dict[str, bool] = {}
        self.performance_metrics: Dict[str, Dict] = {}
    
    def add_provider(self, name: str, provider: LLMProvider, priority: int = 0):
        """Add a provider to the manager"""
        
        self.providers[name] = provider
        self.health_status[name] = True
        self.performance_metrics[name] = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_latency": 0.0,
            "error_rate": 0.0
        }
        
        # Insert provider in priority order
        self.provider_priority.insert(priority, name)
    
    def remove_provider(self, name: str):
        """Remove a provider from the manager"""
        if name in self.providers:
            del self.providers[name]
            del self.health_status[name]
            del self.performance_metrics[name]
            if name in self.provider_priority:
                self.provider_priority.remove(name)
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    async def generate(self, request: GenerationRequest, preferred_provider: Optional[str] = None) -> Dict[str, Any]:
        """Generate response with automatic failover"""
        
        providers_to_try = []
        
        # Try preferred provider first if specified and healthy
        if preferred_provider and preferred_provider in self.providers:
            if self.health_status.get(preferred_provider, False):
                providers_to_try.append(preferred_provider)
        
        # Add other providers in priority order
        for provider_name in self.provider_priority:
            if provider_name not in providers_to_try and self.health_status.get(provider_name, False):
                providers_to_try.append(provider_name)
        
        last_exception = None
        
        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                
                start_time = time.time()
                result = await provider.generate(request)
                latency = time.time() - start_time
                
                # Update performance metrics
                await self._update_metrics(provider_name, latency, True)
                
                result["provider_used"] = provider_name
                result["latency_ms"] = latency * 1000
                
                return result
                
            except Exception as e:
                last_exception = e
                logging.warning(f"Provider {provider_name} failed: {str(e)}")
                
                # Update metrics and health status
                await self._update_metrics(provider_name, 0, False)
                await self._check_provider_health(provider_name)
                
                continue
        
        # All providers failed
        raise Exception(f"All providers failed. Last error: {str(last_exception)}")
    
    async def _update_metrics(self, provider_name: str, latency: float, success: bool):
        """Update performance metrics for a provider"""
        
        metrics = self.performance_metrics[provider_name]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            # Update average latency using exponential moving average
            alpha = 0.1
            metrics["average_latency"] = (
                alpha * latency + (1 - alpha) * metrics["average_latency"]
            )
        
        # Update error rate
        metrics["error_rate"] = 1 - (metrics["successful_requests"] / metrics["total_requests"])
    
    async def _check_provider_health(self, provider_name: str):
        """Check and update provider health status"""
        
        metrics = self.performance_metrics[provider_name]
        
        # Mark as unhealthy if error rate is too high
        if metrics["error_rate"] > 0.5 and metrics["total_requests"] > 10:
            self.health_status[provider_name] = False
            logging.warning(f"Provider {provider_name} marked as unhealthy")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "providers": list(self.providers.keys()),
            "health_status": self.health_status.copy(),
            "performance_metrics": self.performance_metrics.copy(),
            "provider_priority": self.provider_priority.copy()
        }
    
    def mark_provider_healthy(self, provider_name: str):
        """Manually mark a provider as healthy"""
        if provider_name in self.providers:
            self.health_status[provider_name] = True
          
