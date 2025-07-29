# LLM review logic will go here

import os
from providers.registry import ProviderRegistry
from config import get_openai_api_key, get_gemini_api_key

def load_prompt_template(mode, prompts_dir=None):
    """
    Load a prompt template file (Markdown/Plaintext) from the prompts directory.
    mode: e.g. 'security', 'accessibility', 'performance', 'quality'
    """
    if prompts_dir is None:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompts_dir = os.path.join(script_dir, "prompts")
    
    filename = f"{mode}.md"
    path = os.path.join(prompts_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_base_prompt(prompts_dir=None):
    """
    Load the base prompt template that contains common instructions.
    """
    if prompts_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompts_dir = os.path.join(script_dir, "prompts")
    
    base_path = os.path.join(prompts_dir, "base.md")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Base prompt template not found: {base_path}")
    with open(base_path, "r", encoding="utf-8") as f:
        return f.read()

def combine_prompt_templates(modes, prompts_dir=None):
    """
    Combine the base prompt with specific mode templates for the selected modes.
    Returns a single string with base prompt + all mode-specific prompts.
    """
    # Load base prompt first
    base_prompt = load_base_prompt(prompts_dir=prompts_dir)
    
    # Load mode-specific prompts
    mode_prompts = []
    for mode in modes:
        mode_prompts.append(load_prompt_template(mode, prompts_dir=prompts_dir))
    
    # Combine: base prompt + mode-specific sections
    if mode_prompts:
        return f"{base_prompt}\n\n{chr(10).join(mode_prompts)}"
    else:
        return base_prompt

def build_final_prompt(modes, diff, prompts_dir=None, max_diff_length=8000):
    """
    Combine prompt templates for the selected modes and inject the diff with clean formatting.
    Warn if the diff is overly large, but do not truncate by default.
    """
    prompt = combine_prompt_templates(modes, prompts_dir=prompts_dir)
    warning = ""
    if len(diff) > max_diff_length:
        warning = f"\n\n⚠️ Warning: Diff is very large ({len(diff)} chars). LLM may not process the full context."
    
    # Enhanced formatting with line number guidance
    formatted = f"""{prompt}

---

## REVIEW MODES ACTIVE
{', '.join([f"**{mode.upper()}**" for mode in modes])}

---

### Git Diff Analysis

**IMPORTANT:** Pay close attention to the line numbers in the @@ headers and use them for accurate line number reporting.

```diff
{diff}
```{warning}"""
    
    return formatted

def call_llm(prompt, provider="chatgpt", model=None):
    """
    Send the prompt to the selected LLM provider using the new modular system.
    provider: 'chatgpt', 'gemini', 'claude', 'copilot', etc.
    model: model name to use (overrides default)
    Returns the parsed response or raises an error.
    """
    
    # Get API key based on provider
    api_key = None
    if provider == "chatgpt":
        api_key = get_openai_api_key()
    elif provider == "gemini":
        api_key = get_gemini_api_key()
    # claude and copilot handle their own API keys
    
    try:
        # Get provider instance from registry
        llm_provider = ProviderRegistry.get_provider(provider, api_key)
        
        # Generate response
        response = llm_provider.generate_response(prompt, model)
        
        return response
        
    except Exception as e:
        raise RuntimeError(f"{provider.title()} provider failed: {e}")
