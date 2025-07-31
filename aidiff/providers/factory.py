"""LLM provider factory."""

from typing import Dict, Type
from aidiff.providers import LLMProvider
from aidiff.providers.openai_provider import OpenAIProvider
from aidiff.providers.google_provider import GoogleProvider
from aidiff.providers.anthropic_provider import AnthropicProvider
from aidiff.core.exceptions import LLMError


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: Dict[str, Type[LLMProvider]] = {
        "chatgpt": OpenAIProvider,
        "gemini": GoogleProvider,
        "claude": AnthropicProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, api_key: str) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider ("openai", "google", etc.)
            api_key: API key for the provider
            
        Returns:
            Configured LLM provider instance
            
        Raises:
            LLMError: If provider is not supported
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise LLMError(f"Provider '{provider_name}' is not supported. Available: {available}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key)

    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported provider names."""
        return list(cls._providers.keys())
