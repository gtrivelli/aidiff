"""Configuration loader utility."""

import os
from dotenv import load_dotenv
from aidiff.core.exceptions import ConfigError


class ConfigLoader:
    """Handles loading configuration from environment variables."""

    def __init__(self):
        """Initialize and load environment variables."""
        load_dotenv()

    def get_openai_api_key(self) -> str:
        """
        Get OpenAI API key from environment.
        
        Returns:
            API key string
            
        Raises:
            ConfigError: If API key is not found
        """
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ConfigError(
                "OPENAI_API_KEY not found. Please set it in your .env file or environment variables."
            )
        return key

    def get_gemini_api_key(self) -> str:
        """
        Get Gemini API key from environment.
        
        Returns:
            API key string
            
        Raises:
            ConfigError: If API key is not found
        """
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ConfigError(
                "GEMINI_API_KEY not found. Please set it in your .env file or environment variables."
            )
        return key

    def get_anthropic_api_key(self) -> str:
        """
        Get Anthropic API key from environment.
        
        Returns:
            API key string
            
        Raises:
            ConfigError: If API key is not found
        """
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ConfigError(
                "ANTHROPIC_API_KEY not found. Please set it in your .env file or environment variables."
            )
        return key

    def get_api_key_for_provider(self, provider: str) -> str:
        """
        Get API key for the specified provider.
        
        Args:
            provider: Provider name ("chatgpt", "gemini", "claude")
            
        Returns:
            API key string
            
        Raises:
            ConfigError: If provider is not supported or API key is not found
        """
        key_getters = {
            "chatgpt": self.get_openai_api_key,
            "gemini": self.get_gemini_api_key,
            "claude": self.get_anthropic_api_key,
        }
        
        if provider not in key_getters:
            supported = ", ".join(key_getters.keys())
            raise ConfigError(f"Provider '{provider}' is not supported. Available: {supported}")
        
        return key_getters[provider]()
