"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            model: Optional model name override
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If the API call fails
        """
        pass

    @abstractmethod
    def get_default_models(self) -> tuple:
        """Get default model preferences for this provider."""
        pass
