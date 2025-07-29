"""
Google Gemini Provider
"""
import os
import requests
from typing import Optional, List
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv('GEMINI_API_KEY'))
    
    def get_name(self) -> str:
        return "Gemini"
    
    def get_default_models(self) -> List[str]:
        # Use the newer 2.0-flash model for better performance
        # Also keep 1.5-flash as backup option
        return ["gemini-2.0-flash", "gemini-1.5-flash"]
    
    def validate_api_key(self) -> bool:
        return bool(self.api_key)
    
    def call_api(self, prompt: str, model: Optional[str] = None) -> str:
        model_name = model or self.get_default_models()[0]
        
        # Remove leading 'models/' if present
        if model_name.startswith("models/"):
            model_name = model_name[len("models/"):]
        
        # Use the v1beta endpoint which supports newer models like gemini-2.0-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key  # Use header instead of query parameter
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            # Use configurable timeout (default 30s for better UX)
            timeout = int(os.getenv('AUTODIFF_TIMEOUT', '30'))
            resp = requests.post(url, headers=headers, json=data, timeout=timeout)
            resp.raise_for_status()
            
            result = resp.json()
            content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not content or not content.strip():
                raise ValueError("Gemini response is empty")
                
            return content
            
        except requests.exceptions.Timeout as e:
            # Timeout errors - mark as network issue, not quota
            timeout = int(os.getenv('AUTODIFF_TIMEOUT', '30'))
            timeout_error = RuntimeError(f"Gemini API timeout ({timeout}s): The request took too long to complete. This might be due to a large diff or network issues. Try setting AUTODIFF_TIMEOUT environment variable to a higher value.")
            timeout_error.is_network_issue = True
            raise timeout_error
            
        except requests.exceptions.ConnectionError as e:
            # Connection errors - mark as network issue
            connection_error = RuntimeError(f"Gemini API connection error: Unable to connect to Gemini servers. Check your internet connection.")
            connection_error.is_network_issue = True
            raise connection_error
            
        except requests.HTTPError as e:
            if resp.status_code == 404:
                raise RuntimeError(f"Gemini model '{model_name}' not found. Try using 'models/gemini-1.5-flash' or check the Gemini API documentation.")
            elif resp.status_code == 429:
                # For quota limits, don't retry with other models since it's account-wide
                quota_error = RuntimeError(f"Gemini API quota exceeded: {e}. Response: {resp.text}")
                quota_error.is_quota_limit = True  # Add flag to identify quota errors
                raise quota_error
            elif resp.status_code >= 500:
                # Server errors - mark as temporary issue
                server_error = RuntimeError(f"Gemini API server error ({resp.status_code}): {e}. This is likely a temporary issue with Google's servers.")
                server_error.is_server_issue = True
                raise server_error
            else:
                raise RuntimeError(f"Gemini API error: {e}. Response: {resp.text}")
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
