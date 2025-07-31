"""
Provider Registry for LLM providers
"""
from typing import Dict, Type, Optional
from .base import LLMProvider
from .chatgpt import ChatGPTProvider
from .gemini import GeminiProvider
from .claude import ClaudeProvider

class ProviderRegistry:
    """Registry for managing LLM providers"""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        'chatgpt': ChatGPTProvider,
        'gemini': GeminiProvider,
        'claude': ClaudeProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by name"""
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(f"Unknown provider '{provider_name}'. Available providers: {available}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key)
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """List all available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """Register a new provider (for future extensibility)"""
        cls._providers[name] = provider_class
