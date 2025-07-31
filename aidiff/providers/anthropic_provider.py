"""Anthropic Claude provider for LLM operations."""

import os
from typing import List, Optional
from aidiff.providers import LLMProvider
from aidiff.core.exceptions import LLMError


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Default model

    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt
            model: Optional model override
            
        Returns:
            Generated response
            
        Raises:
            LLMError: If API call fails
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=model or self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except ImportError:
            raise LLMError("anthropic package is not installed. Install with: pip install anthropic")
        except Exception as e:
            raise LLMError(f"Anthropic API error: {e}")

    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
