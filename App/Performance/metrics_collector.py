"""
Performance criteria validation module
"""
from typing import Dict, Any
from performance_monitor import PerformanceMonitor, PerformanceMetrics


class PerformanceCriteriaValidator:
    """Validate performance against defined criteria"""
    
    def __init__(self):
        self.criteria = {
            "module_generation_time": 30,  # seconds
            "application_generation_time": 300,  # seconds
            "generation_success_rate": 0.95,  # 95%
            "integration_success_rate": 0.90,  # 90%
            "max_cpu_usage": 80,  # 80%
            "max_memory_usage": 90  # 90%
        }
    
    def validate_module_generation(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Validate module generation performance"""
        
        duration = metrics.end_time - metrics.start_time if metrics.end_time else float('inf')
        cpu_usage = max(metrics.cpu_usage_start, metrics.cpu_usage_end)
        memory_usage = max(metrics.memory_usage_start, metrics.memory_usage_end)
        
        return {
            "time_criteria_met": duration <= self.criteria["module_generation_time"],
            "cpu_criteria_met": cpu_usage <= self.criteria["max_cpu_usage"],
            "memory_criteria_met": memory_usage <= self.criteria["max_memory_usage"],
            "success_criteria_met": metrics.success
        }
    
    def validate_application_generation(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Validate application generation performance"""
        
        duration = metrics.end_time - metrics.start_time if metrics.end_time else float('inf')
        cpu_usage = max(metrics.cpu_usage_start, metrics.cpu_usage_end)
        memory_usage = max(metrics.memory_usage_start, metrics.memory_usage_end)
        
        return {
            "time_criteria_met": duration <= self.criteria["application_generation_time"],
            "cpu_criteria_met": cpu_usage <= self.criteria["max_cpu_usage"],
            "memory_criteria_met": memory_usage <= self.criteria["max_memory_usage"],
            "success_criteria_met": metrics.success
        }
    
    def validate_overall_performance(self, monitor: PerformanceMonitor) -> Dict[str, Any]:
        """Validate overall system performance"""
        
        module_stats = monitor.get_performance_stats("module_generation")
        app_stats = monitor.get_performance_stats("application_generation")
        integration_stats = monitor.get_performance_stats("module_integration")
        
        validation_results = {
            "module_generation": {
                "avg_time_ok": module_stats.get("avg_duration", 0) <= self.criteria["module_generation_time"],
                "success_rate_ok": module_stats.get("success_rate", 0) >= self.criteria["generation_success_rate"]
            },
            "application_generation": {
                "avg_time_ok": app_stats.get("avg_duration", 0) <= self.criteria["application_generation_time"],
                "success_rate_ok": app_stats.get("success_rate", 0) >= self.criteria["generation_success_rate"]
            },
            "integration": {
                "success_rate_ok": integration_stats.get("success_rate", 0) >= self.criteria["integration_success_rate"]
            }
        }
        
        return validation_results
    
    def update_criteria(self, new_criteria: Dict[str, Any]):
        """Update performance criteria"""
        self.criteria.update(new_criteria)
    
    def get_criteria(self) -> Dict[str, Any]:
        """Get current performance criteria"""
        return self.criteria.copy()
