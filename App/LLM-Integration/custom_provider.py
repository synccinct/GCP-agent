"""Custom provider implementation for extending the framework"""

import aiohttp
from typing import Dict, Any, AsyncGenerator, Callable, Optional

from .base import LLMProvider, GenerationRequest

class CustomProvider(LLMProvider):
    """Custom provider for implementing non-standard APIs"""
    
    def __init__(self, credentials, 
                 request_formatter: Callable[[GenerationRequest], Dict[str, Any]],
                 response_parser: Callable[[Dict[str, Any]], Dict[str, Any]],
                 endpoint_url: str,
                 headers_builder: Optional[Callable[[str], Dict[str, str]]] = None):
        """
        Initialize custom provider with user-defined formatters
        
        Args:
            credentials: API credentials
            request_formatter: Function to format requests for the custom API
            response_parser: Function to parse responses from the custom API
            endpoint_url: The API endpoint URL
            headers_builder: Optional function to build request headers
        """
        super().__init__(credentials)
        self.request_formatter = request_formatter
        self.response_parser = response_parser
        self.endpoint_url = endpoint_url
        self.headers_builder = headers_builder or self._default_headers_builder
    
    def _default_headers_builder(self, api_key: str) -> Dict[str, str]:
        """Default headers builder"""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate response using custom API"""
        
        await self.rate_limiter.acquire(request.max_tokens)
        
        headers = self.headers_builder(self.credentials.api_key)
        payload = self.format_request(request)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint_url,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Custom API error: {response.status} - {error_text}")
                
                result = await response.json()
                return self._parse_response(result)
    
    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using custom API"""
        # Basic implementation - can be overridden
        raise NotImplementedError("Streaming not implemented for custom provider")
    
    def format_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Format request using custom formatter"""
        return self.request_formatter(request)
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse response using custom parser"""
        return self.response_parser(response)
      
