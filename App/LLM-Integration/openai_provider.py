"""OpenAI API provider implementation"""

import json
import aiohttp
from typing import Dict, Any, AsyncGenerator

from .base import LLMProvider, GenerationRequest

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self.base_url = "https://api.openai.com/v1"
    
    async def generate(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        
        await self.rate_limiter.acquire(request.max_tokens)
        
        headers = {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.credentials.organization:
            headers["OpenAI-Organization"] = self.credentials.organization
        
        payload = self.format_request(request)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                
                result = await response.json()
                return self._parse_response(result)
    
    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API"""
        
        await self.rate_limiter.acquire(request.max_tokens)
        
        headers = {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = self.format_request(request)
        payload["stream"] = True
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            content = chunk['choices'][0]['delta'].get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    
    def format_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Format request for OpenAI API"""
        
        messages = []
        
        if request.system_message:
            messages.append({
                "role": "system",
                "content": request.system_message
            })
        
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = "auto"
        
        return payload
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAI response into standardized format"""
        return {
            "content": response["choices"][0]["message"]["content"],
            "usage": response.get("usage", {}),
            "model": response.get("model"),
            "finish_reason": response["choices"][0].get("finish_reason"),
            "raw_response": response
      }
      
