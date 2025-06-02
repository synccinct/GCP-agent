"""Anthropic Claude API provider implementation"""

import aiohttp
from typing import Dict, Any, AsyncGenerator

from .base import LLMProvider, GenerationRequest

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider implementation"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate response using Anthropic API"""
        
        await self.rate_limiter.acquire(request.max_tokens)
        
        headers = {
            "x-api-key": self.credentials.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = self.format_request(request)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                
                result = await response.json()
                return self._parse_response(result)
    
    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic API"""
        # Implementation for streaming would go here
        # Anthropic supports streaming via Server-Sent Events
        raise NotImplementedError("Streaming not yet implemented for Anthropic")
    
    def format_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Format request for Anthropic API"""
        
        messages = []
        
        if request.system_message:
            system = request.system_message
        else:
            system = "You are a helpful AI assistant."
        
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        return {
            "model": request.model,
            "system": system,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Anthropic response into standardized format"""
        return {
            "content": response["content"][0]["text"],
            "usage": response.get("usage", {}),
            "model": response.get("model"),
            "finish_reason": response.get("stop_reason"),
            "raw_response": response
        }
      
