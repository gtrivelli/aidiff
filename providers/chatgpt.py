"""
ChatGPT (OpenAI) Provider
"""
import os
import openai
from typing import Optional, List
from .base import LLMProvider

class ChatGPTProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if self.api_key:
            openai.api_key = self.api_key
        elif os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def get_name(self) -> str:
        return "ChatGPT"
    
    def get_default_models(self) -> List[str]:
        # Use 3.5-turbo first for lower cost and quota usage
        # 4-turbo is more powerful but more expensive
        return ["gpt-3.5-turbo", "gpt-4-turbo"]
    
    def validate_api_key(self) -> bool:
        return bool(openai.api_key)
    
    def call_api(self, prompt: str, model: Optional[str] = None) -> str:
        model_name = model or self.get_default_models()[0]
        
        try:
            response = openai.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2048,
                timeout=30  # 30 second timeout
            )
            
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("ChatGPT response is empty")
            
            return content
            
        except openai.RateLimitError as e:
            # For rate limits, don't retry with other models since it's account-wide
            rate_limit_error = RuntimeError(f"OpenAI API rate limit exceeded: {e}")
            rate_limit_error.is_quota_limit = True  # Add flag to identify quota errors
            raise rate_limit_error
            
        except (openai.APIConnectionError, openai.APITimeoutError) as e:
            # Network/timeout errors - mark as network issue
            network_error = RuntimeError(f"OpenAI API network error: {e}. Check your internet connection or try again later.")
            network_error.is_network_issue = True
            raise network_error
            
        except openai.InternalServerError as e:
            # Server errors - mark as temporary issue
            server_error = RuntimeError(f"OpenAI API server error: {e}. This is likely a temporary issue with OpenAI's servers.")
            server_error.is_server_issue = True
            raise server_error
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")
