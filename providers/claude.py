"""
Claude (Anthropic) Provider
"""
import os
import anthropic
from typing import Optional, List
from .base import LLMProvider

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv('ANTHROPIC_API_KEY'))
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
    
    def get_name(self) -> str:
        return "Claude"
    
    def get_default_models(self) -> List[str]:
        # Use Claude 3.5 Sonnet as primary (best balance of speed/quality)
        # Claude 3 Haiku as backup (faster, lower cost)
        return ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    
    def validate_api_key(self) -> bool:
        return bool(self.api_key and self.client)
    
    def call_api(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.client:
            raise ValueError("Claude API key is not configured")
            
        model_name = model or self.get_default_models()[0]
        
        try:
            response = self.client.messages.create(
                model=model_name,
                max_tokens=2048,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract text content from the response
            content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text
            
            if not content or not content.strip():
                raise ValueError("Claude response is empty")
            
            return content
            
        except anthropic.RateLimitError as e:
            # For rate limits, don't retry with other models since it's account-wide
            rate_limit_error = RuntimeError(f"Anthropic API rate limit exceeded: {e}")
            rate_limit_error.is_quota_limit = True  # Add flag to identify quota errors
            raise rate_limit_error
            
        except anthropic.APITimeoutError as e:
            timeout_error = RuntimeError(f"Claude API timeout: {e}")
            timeout_error.is_timeout = True
            raise timeout_error
            
        except anthropic.APIError as e:
            # Handle other API errors (invalid model, server errors, etc.)
            if e.status_code in [500, 502, 503, 504]:
                server_error = RuntimeError(f"Claude server error ({e.status_code}): {e}")
                server_error.is_server_error = True
                raise server_error
            elif e.status_code == 401:
                auth_error = RuntimeError(f"Claude authentication failed: Invalid API key")
                auth_error.is_auth_error = True
                raise auth_error
            else:
                raise RuntimeError(f"Claude API error ({e.status_code}): {e}")
                
        except Exception as e:
            # Catch any other unexpected errors
            raise RuntimeError(f"Unexpected Claude API error: {e}")
