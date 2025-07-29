"""OpenAI LLM provider implementation."""

import openai
from typing import Optional, Tuple
from aidiff.providers import LLMProvider
from aidiff.core.exceptions import LLMError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.api_key = api_key
        openai.api_key = api_key

    def get_default_models(self) -> Tuple[str, ...]:
        """Get default model preferences."""
        return ("gpt-4-turbo", "gpt-3.5-turbo")

    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate response using OpenAI's API.
        
        Args:
            prompt: Input prompt
            model: Model name (optional)
            
        Returns:
            Generated response
            
        Raises:
            LLMError: If API call fails
        """
        models = [model] if model else list(self.get_default_models())
        last_error = None

        for m in models:
            try:
                response = openai.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=2048
                )
                content = response.choices[0].message.content
                
                if not content.strip():
                    raise ValueError("LLM response is empty.")
                
                return content
            except Exception as e:
                last_error = e
                continue

        raise LLMError(f"All OpenAI model calls failed. Last error: {last_error}")
