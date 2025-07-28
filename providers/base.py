"""
Base class for LLM providers
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the provider name"""
        pass
    
    @abstractmethod
    def get_default_models(self) -> List[str]:
        """Return list of default models to try, in order of preference"""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Check if API key is available and valid"""
        pass
    
    @abstractmethod
    def call_api(self, prompt: str, model: Optional[str] = None) -> str:
        """Make API call and return response"""
        pass
    
    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """Main entry point for generating responses"""
        if not self.validate_api_key():
            raise RuntimeError(f"{self.get_name()} API key not found or invalid")
        
        models_to_try = [model] if model else self.get_default_models()
        last_error = None
        
        for model_name in models_to_try:
            try:
                response = self.call_api(prompt, model_name)
                if response and response.strip():
                    return response
                else:
                    raise ValueError(f"Empty response from {model_name}")
            except Exception as e:
                last_error = e
                # If this is a quota limit error, don't try other models
                if hasattr(e, 'is_quota_limit') and e.is_quota_limit:
                    raise e
                # If this is a network/timeout/server issue, don't try other models either
                # since it's likely to affect all models from the same provider
                if hasattr(e, 'is_network_issue') and e.is_network_issue:
                    raise e
                if hasattr(e, 'is_server_issue') and e.is_server_issue:
                    raise e
                continue
        
        raise RuntimeError(f"All {self.get_name()} model calls failed. Last error: {last_error}")
