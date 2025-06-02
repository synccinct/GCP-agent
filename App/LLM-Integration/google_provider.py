"""Google Gemini API provider implementation"""

import aiohttp
from typing import Dict, Any, AsyncGenerator

from .base import LLMProvider, GenerationRequest

class GoogleProvider(LLMProvider):
    """Google Gemini API provider implementation"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta"
    
    async def generate(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate response using Google Gemini API"""
        
        await self.rate_limiter.acquire(request.max_tokens)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = self.format_request(request)
        url = f"{self.base_url}/models/{request.model}:generateContent?key={self.credentials.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Google API error: {response.status} - {error_text}")
                
                result = await response.json()
                return self._parse_response(result)
    
    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using Google Gemini API"""
        # Implementation for streaming would go here
        raise NotImplementedError("Streaming not yet implemented for Google")
    
    def format_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Format request for Google Gemini API"""
        
        contents = []
        
        if request.system_message:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System: {request.system_message}"}]
            })
        
        contents.append({
            "role": "user",
            "parts": [{"text": request.prompt}]
        })
        
        return {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": request.temperature
            }
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google response into standardized format"""
        candidate = response["candidates"][0]
        return {
            "content": candidate["content"]["parts"][0]["text"],
            "usage": response.get("usageMetadata", {}),
            "model": "gemini",
            "finish_reason": candidate.get("finishReason"),
            "raw_response": response
        }
      
