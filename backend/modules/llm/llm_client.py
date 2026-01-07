"""
OpenRouter API client for LLM interactions.

Uses Gemini 2.5 Flash via OpenRouter for keyword extraction and article categorization.
"""

import httpx
from pydantic import BaseModel
from typing import Any


class OpenRouterClient:
    """Async client for OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "google/gemini-2.5-flash-preview"
    
    def __init__(self, api_key: str, model: str | None = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (defaults to Gemini 2.5 Flash)
        """
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            response_format: Optional JSON schema for structured output
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            The API response as a dict
        """
        client = await self._get_client()
        
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    async def get_completion_text(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Get the text content from a chat completion.
        
        Args:
            messages: List of message dicts
            response_format: Optional JSON schema
            temperature: Sampling temperature
            
        Returns:
            The assistant's response text
        """
        result = await self.chat_completion(
            messages=messages,
            response_format=response_format,
            temperature=temperature,
        )
        
        return result["choices"][0]["message"]["content"]


class Message(BaseModel):
    """Chat message model."""
    role: str
    content: str


def create_messages(system: str, user: str) -> list[dict[str, str]]:
    """
    Create a simple system + user message list.
    
    Args:
        system: System prompt
        user: User message
        
    Returns:
        List of message dicts
    """
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
