"""Google Gemini LLM provider implementation."""

import requests
from typing import Optional, Tuple
from aidiff.providers import LLMProvider
from aidiff.core.exceptions import LLMError


class GoogleProvider(LLMProvider):
    """Google Gemini provider implementation."""

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.api_key = api_key

    def get_default_models(self) -> Tuple[str, ...]:
        """Get default model preferences."""
        return ("gemini-1.5-flash",)

    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate response using Google's Gemini API.
        
        Args:
            prompt: Input prompt
            model: Model name (optional)
            
        Returns:
            Generated response
            
        Raises:
            LLMError: If API call fails
        """
        model_name = model or self.get_default_models()[0]
        
        # Remove leading 'models/' if present
        if model_name.startswith("models/"):
            model_name = model_name[len("models/"):]
        
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {"key": self.api_key}
        
        try:
            resp = requests.post(url, headers=headers, params=params, json=data, timeout=60)
            
            try:
                resp.raise_for_status()
            except requests.HTTPError as e:
                error_msg = f"Gemini API error: {resp.text}"
                if resp.status_code == 404:
                    error_msg += f"\nModel '{model_name}' not found. Try using a valid Gemini model."
                raise LLMError(error_msg)
            
            result = resp.json()
            content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not content.strip():
                raise ValueError("Gemini response is empty.")
            
            return content
            
        except requests.RequestException as e:
            raise LLMError(f"Gemini API request failed: {e}")
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}")
