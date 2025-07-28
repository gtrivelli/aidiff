"""
Copilot Provider - Coming Soon
"""
from typing import Optional, List
from .base import LLMProvider

class CopilotProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
    
    def get_name(self) -> str:
        return "GitHub Copilot"
    
    def get_default_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4"]
    
    def validate_api_key(self) -> bool:
        # Copilot doesn't use traditional API keys
        return True
    
    def call_api(self, prompt: str, model: Optional[str] = None) -> str:
        # Generate mock response for demonstration
        print("ℹ️  GitHub Copilot provider selected, but not yet implemented.")
        print("ℹ️  Generating mock security analysis for demonstration...")
        
        return """---
**Issue:** Use of eval() function with user input
**File:** test.js
**Line Number:** 4
**Code:** eval(userInput); // This should be flagged by security review
**Severity:** Critical
**Confidence:** 95%
**Suggestion:** Replace eval() with safer alternatives like JSON.parse() for data or use a sandboxed execution environment. Never execute user input directly.
---"""
