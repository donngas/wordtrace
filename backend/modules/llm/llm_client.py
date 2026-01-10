"""
OpenRouter API client for LLM interactions.

Uses Gemini 2.5 Flash via OpenRouter for keyword extraction and article categorization.
"""

from openai import AsyncOpenAI
from typing import Any

from common.schema import Message


class OpenRouterClient:
    """Async client for OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite-preview-09-2025"
    
    def __init__(self, api_key: str, model: str | None = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (defaults to Gemini 2.5 Flash)
        """
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
        )
    
    async def close(self) -> None:
        """Close the client."""
        await self._client.close()
    
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
        # Convert response_format for OpenAI SDK if needed
        # OpenAI SDK expects just the dict usually, but let's pass it through
        # Note: OpenRouter supports OpenAI's response_format
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
            
        response = await self._client.chat.completions.create(**kwargs)
        
        # Convert to dict to match previous return type style exactly or return object?
        # The previous code returned `response.json()` which is a dict.
        # OpenAI SDK returns a Pydantic model. We should convert it to dict for compatibility.
        return response.model_dump()
    
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
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
            
        response = await self._client.chat.completions.create(**kwargs)
        
        content = response.choices[0].message.content
        return content or ""





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
