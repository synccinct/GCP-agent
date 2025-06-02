"""Token bucket rate limiter for API requests"""

import asyncio
import time

class RateLimiter:
    """Token bucket rate limiter for API requests"""
    
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.rpm_limit = requests_per_minute
        self.tpm_limit = tokens_per_minute
        self.request_tokens = requests_per_minute
        self.token_tokens = tokens_per_minute
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, token_count: int = 1):
        """Acquire tokens for rate limiting"""
        
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_refill
            
            # Refill tokens based on time passed
            self.request_tokens = min(
                self.rpm_limit,
                self.request_tokens + (time_passed * self.rpm_limit / 60)
            )
            self.token_tokens = min(
                self.tpm_limit,
                self.token_tokens + (time_passed * self.tpm_limit / 60)
            )
            
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.request_tokens < 1 or self.token_tokens < token_count:
                # Calculate wait time
                request_wait = (1 - self.request_tokens) * 60 / self.rpm_limit
                token_wait = (token_count - self.token_tokens) * 60 / self.tpm_limit
                wait_time = max(request_wait, token_wait)
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire(token_count)
            
            # Consume tokens
            self.request_tokens -= 1
            self.token_tokens -= token_count
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limiter status"""
        return {
            "request_tokens_available": self.request_tokens,
            "token_tokens_available": self.token_tokens,
            "rpm_limit": self.rpm_limit,
            "tpm_limit": self.tpm_limit
        }
    
    def reset(self):
        """Reset rate limiter to full capacity"""
        self.request_tokens = self.rpm_limit
        self.token_tokens = self.tpm_limit
        self.last_refill = time.time()
      
