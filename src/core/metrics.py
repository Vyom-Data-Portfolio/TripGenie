"""
Cost tracking and metrics monitoring
Critical for production ML systems
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class RequestMetrics:
    """Track individual request metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    operation: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None

class MetricsTracker:
    """
    Production-grade metrics tracking
    - Cost monitoring
    - Latency tracking
    - Success rate
    - Token usage
    """
    
    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self._start_time: Optional[float] = None
        
    def start_request(self) -> None:
        """Start timing a request"""
        self._start_time = time.time()
        
    def end_request(
        self,
        operation: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        success: bool = True,
        error: Optional[str] = None
    ) -> RequestMetrics:
        """End request and calculate metrics"""
        latency = (time.time() - self._start_time) * 1000 if self._start_time else 0
        
        # Calculate cost (Claude Sonnet 4 pricing)
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost
        
        metrics = RequestMetrics(
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            cost_usd=total_cost,
            success=success,
            error=error
        )
        
        self.requests.append(metrics)
        self._start_time = None
        return metrics
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.requests:
            return {
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "success_rate": 0.0,
                "total_tokens": 0
            }
        
        total_cost = sum(r.cost_usd for r in self.requests)
        avg_latency = sum(r.latency_ms for r in self.requests) / len(self.requests)
        success_rate = sum(1 for r in self.requests if r.success) / len(self.requests)
        total_tokens = sum(r.input_tokens + r.output_tokens for r in self.requests)
        
        return {
            "total_requests": len(self.requests),
            "total_cost_usd": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate * 100, 2),
            "total_tokens": total_tokens,
            "cost_per_request": round(total_cost / len(self.requests), 4)
        }
    
    def export_json(self, filepath: str) -> None:
        """Export metrics to JSON"""
        data = {
            "summary": self.get_summary(),
            "requests": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "operation": r.operation,
                    "model": r.model,
                    "tokens": r.input_tokens + r.output_tokens,
                    "latency_ms": r.latency_ms,
                    "cost_usd": r.cost_usd,
                    "success": r.success
                }
                for r in self.requests
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# Global tracker instance
tracker = MetricsTracker()
