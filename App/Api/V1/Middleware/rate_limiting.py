import time
import asyncio
from typing import Dict, Callable
from fastapi import HTTPException, Request, status
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self.clients: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": 0,
            "last_update": time.time()
        })
    
    async def is_allowed(self, identifier: str, requests_per_minute: int = 60) -> bool:
        """Check if request is allowed under rate limit"""
        
        now = time.time()
        client = self.clients[identifier]
        
        # Calculate tokens to add based on time passed
        time_passed = now - client["last_update"]
        tokens_to_add = time_passed * (requests_per_minute / 60.0)
        
        # Update client state
        client["tokens"] = min(requests_per_minute, client["tokens"] + tokens_to_add)
        client["last_update"] = now
        
        # Check if request is allowed
        if client["tokens"] >= 1:
            client["tokens"] -= 1
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(requests_per_minute: int = 60):
    """Rate limiting dependency factory"""
    
    async def rate_limit_dependency(request: Request):
        # Use IP address as identifier (in production, use user ID)
        client_ip = request.client.host
        
        if not await rate_limiter.is_allowed(client_ip, requests_per_minute):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
    
    return rate_limit_dependency

class AdvancedRateLimiter:
    """Advanced rate limiter with different strategies"""
    
    def __init__(self):
        self.sliding_windows: Dict[str, list] = defaultdict(list)
        self.token_buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": 0,
            "last_refill": time.time()
        })
    
    async def sliding_window_check(self, identifier: str, requests_per_window: int, window_seconds: int) -> bool:
        """Sliding window rate limiting"""
        
        now = time.time()
        window = self.sliding_windows[identifier]
        
        # Remove old requests outside the window
        cutoff_time = now - window_seconds
        self.sliding_windows[identifier] = [req_time for req_time in window if req_time > cutoff_time]
        
        # Check if under limit
        if len(self.sliding_windows[identifier]) < requests_per_window:
            self.sliding_windows[identifier].append(now)
            return True
        
        return False
    
    async def token_bucket_check(self, identifier: str, requests_per_minute: int, burst_size: int = None) -> bool:
        """Token bucket rate limiting with burst support"""
        
        if burst_size is None:
            burst_size = requests_per_minute
        
        now = time.time()
        bucket = self.token_buckets[identifier]
        
        # Refill tokens
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * (requests_per_minute / 60.0)
        bucket["tokens"] = min(burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if request allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False

# Advanced rate limiter instance
advanced_rate_limiter = AdvancedRateLimiter()

def advanced_rate_limit(requests_per_minute: int = 60, burst_size: int = None, use_sliding_window: bool = False):
    """Advanced rate limiting dependency"""
    
    async def advanced_rate_limit_dependency(request: Request):
        client_ip = request.client.host
        
        if use_sliding_window:
            allowed = await advanced_rate_limiter.sliding_window_check(
                client_ip, requests_per_minute, 60
            )
        else:
            allowed = await advanced_rate_limiter.token_bucket_check(
                client_ip, requests_per_minute, burst_size
            )
        
        if not allowed:
            logger.warning(f"Advanced rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
    
    return advanced_rate_limit_dependency
      
