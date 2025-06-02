# observability_manager.py
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class ObservabilityManager:
    """Manages observability, monitoring, and performance tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[Dict]] = {}
        self.traces: List[Dict] = []
    
    def record_metric(self, metric_name: str, value: float, unit: str, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "unit": unit,
            "timestamp": time.time(),
            "tags": tags or {}
        })
        
        self.logger.info(f"Metric recorded: {metric_name}={value}{unit}")
    
    def start_trace(self, operation_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace"""
        trace_id = f"trace_{int(time.time() * 1000)}"
        
        self.traces.append({
            "trace_id": trace_id,
            "operation": operation_name,
            "start_time": time.time(),
            "context": context or {},
            "status": "active"
        })
        
        return trace_id
    
    def end_trace(self, trace_id: str, status: str = "completed", result: Optional[Dict[str, Any]] = None):
        """End a trace"""
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                trace["end_time"] = time.time()
                trace["duration"] = trace["end_time"] - trace["start_time"]
                trace["status"] = status
                trace["result"] = result or {}
                break
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all recorded metrics"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "avg": sum(v["value"] for v in values) / len(values),
                    "min": min(v["value"] for v in values),
                    "max": max(v["value"] for v in values),
                    "unit": values[0]["unit"]
                }
        
        return summary
      
