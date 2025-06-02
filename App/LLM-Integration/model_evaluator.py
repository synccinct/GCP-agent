"""Model evaluation and benchmarking utilities"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .base import GenerationRequest
from .llm_manager import LLMManager

@dataclass
class EvaluationResult:
    """Results from model evaluation"""
    provider_name: str
    model_name: str
    average_latency: float
    success_rate: float
    total_requests: int
    failed_requests: int
    average_tokens_per_second: float
    cost_estimate: Optional[float] = None

class ModelEvaluator:
    """Evaluate and benchmark different models and providers"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.evaluation_history: List[EvaluationResult] = []
    
    async def benchmark_provider(self, 
                                provider_name: str,
                                test_prompts: List[str],
                                model: str,
                                max_tokens: int = 1000,
                                temperature: float = 0.7) -> EvaluationResult:
        """Benchmark a specific provider with test prompts"""
        
        latencies = []
        successes = 0
        failures = 0
        total_tokens = 0
        
        for prompt in test_prompts:
            request = GenerationRequest(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            try:
                start_time = time.time()
                result = await self.llm_manager.generate(request, preferred_provider=provider_name)
                latency = time.time() - start_time
                
                latencies.append(latency)
                successes += 1
                
                # Estimate tokens (rough approximation)
                content_length = len(result.get("content", ""))
                estimated_tokens = content_length // 4  # Rough estimate
                total_tokens += estimated_tokens
                
            except Exception as e:
                failures += 1
                print(f"Request failed: {str(e)}")
        
        total_requests = len(test_prompts)
        avg_latency = statistics.mean(latencies) if latencies else 0
        success_rate = successes / total_requests if total_requests > 0 else 0
        avg_tokens_per_second = (total_tokens / sum(latencies)) if latencies and sum(latencies) > 0 else 0
        
        result = EvaluationResult(
            provider_name=provider_name,
            model_name=model,
            average_latency=avg_latency,
            success_rate=success_rate,
            total_requests=total_requests,
            failed_requests=failures,
            average_tokens_per_second=avg_tokens_per_second
        )
        
        self.evaluation_history.append(result)
        return result
    
    async def compare_providers(self,
                               provider_configs: List[Dict[str, str]],
                               test_prompts: List[str],
                               max_tokens: int = 1000) -> List[EvaluationResult]:
        """Compare multiple providers with the same test prompts"""
        
        results = []
        
        for config in provider_configs:
            provider_name = config["provider_name"]
            model = config["model"]
            
            result = await self.benchmark_provider(
                provider_name=provider_name,
                test_prompts=test_prompts,
                model=model,
                max_tokens=max_tokens
            )
            results.append(result)
        
        return results
    
    def get_best_provider(self, 
                         metric: str = "success_rate",
                         min_requests: int = 5) -> Optional[EvaluationResult]:
        """Get the best performing provider based on specified metric"""
        
        valid_results = [
            r for r in self.evaluation_history 
            if r.total_requests >= min_requests
        ]
        
        if not valid_results:
            return None
        
        if metric == "success_rate":
            return max(valid_results, key=lambda x: x.success_rate)
        elif metric == "latency":
            return min(valid_results, key=lambda x: x.average_latency)
        elif metric == "tokens_per_second":
            return max(valid_results, key=lambda x: x.average_tokens_per_second)
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report"""
        
        if not self.evaluation_history:
            return {"message": "No evaluation data available"}
        
        report = {
            "total_evaluations": len(self.evaluation_history),
            "providers_tested": list(set(r.provider_name for r in self.evaluation_history)),
            "models_tested": list(set(r.model_name for r in self.evaluation_history)),
            "best_by_success_rate": self.get_best_provider("success_rate"),
            "best_by_latency": self.get_best_provider("latency"),
            "best_by_throughput": self.get_best_provider("tokens_per_second"),
            "detailed_results": [
                {
                    "provider": r.provider_name,
                    "model": r.model_name,
                    "success_rate": f"{r.success_rate:.2%}",
                    "avg_latency": f"{r.average_latency:.3f}s",
                    "tokens_per_second": f"{r.average_tokens_per_second:.1f}",
                    "total_requests": r.total_requests
                }
                for r in self.evaluation_history
            ]
        }
        
        return report
      
