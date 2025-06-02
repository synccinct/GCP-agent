"""
Performance monitoring module for tracking system operations
"""
import time
import psutil
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    operation_type: str
    start_time: float
    end_time: Optional[float] = None
    cpu_usage_start: float = 0.0
    cpu_usage_end: float = 0.0
    memory_usage_start: float = 0.0
    memory_usage_end: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, PerformanceMetrics] = {}
    
    def start_operation(self, operation_id: str, operation_type: str) -> PerformanceMetrics:
        """Start tracking an operation"""
        
        metrics = PerformanceMetrics(
            operation_type=operation_type,
            start_time=time.time(),
            cpu_usage_start=psutil.cpu_percent(),
            memory_usage_start=psutil.virtual_memory().percent
        )
        
        self.active_operations[operation_id] = metrics
        return metrics
    
    def end_operation(self, operation_id: str, success: bool = True, error_message: str = None):
        """End tracking an operation"""
        
        if operation_id not in self.active_operations:
            return
        
        metrics = self.active_operations[operation_id]
        metrics.end_time = time.time()
        metrics.cpu_usage_end = psutil.cpu_percent()
        metrics.memory_usage_end = psutil.virtual_memory().percent
        metrics.success = success
        metrics.error_message = error_message
        
        self.metrics_history.append(metrics)
        del self.active_operations[operation_id]
    
    def get_performance_stats(self, operation_type: str = None) -> Dict[str, Any]:
        """Get performance statistics"""
        
        if operation_type:
            relevant_metrics = [m for m in self.metrics_history if m.operation_type == operation_type]
        else:
            relevant_metrics = self.metrics_history
        
        if not relevant_metrics:
            return {}
        
        durations = [m.end_time - m.start_time for m in relevant_metrics if m.end_time]
        success_rate = sum(1 for m in relevant_metrics if m.success) / len(relevant_metrics)
        
        return {
            "total_operations": len(relevant_metrics),
            "success_rate": success_rate,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "avg_cpu_usage": sum(m.cpu_usage_end - m.cpu_usage_start for m in relevant_metrics) / len(relevant_metrics),
            "avg_memory_usage": sum(m.memory_usage_end - m.memory_usage_start for m in relevant_metrics) / len(relevant_metrics)
        }
