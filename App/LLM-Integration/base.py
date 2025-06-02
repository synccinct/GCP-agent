"""Base classes and data structures for LLM providers"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"

@dataclass
class APICredentials:
    """API credentials configuration"""
    provider: ProviderType
    api_key: str
    organization: Optional[str] = None
    project_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100000

@dataclass
class GenerationRequest:
    """Standardized generation request"""
    prompt: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    stream: bool = False
    tools: Optional[List[Dict]] = None
    system_message: Optional[str] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, credentials: APICredentials):
        from .rate_limiter import RateLimiter
        
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(
            credentials.rate_limit_rpm,
            credentials.rate_limit_tpm
        )
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response from LLM"""
        pass
    
    @abstractmethod
    def format_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Format request for specific provider"""
        pass
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse provider-specific response into standardized format"""
        # Default implementation - override in subclasses
        return response
      
