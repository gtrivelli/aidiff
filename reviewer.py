# LLM review logic will go here

import os
import openai
from config import get_openai_api_key
import requests

def load_prompt_template(mode, prompts_dir="prompts"):
    """
    Load a prompt template file (Markdown/Plaintext) from the prompts directory.
    mode: e.g. 'security', 'accessibility', 'performance'
    """
    filename = f"{mode}.md"
    path = os.path.join(prompts_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def combine_prompt_templates(modes, prompts_dir="prompts"):
    """
    Combine multiple prompt templates for the selected modes.
    Returns a single string with all prompts separated by two newlines.
    """
    prompts = []
    for mode in modes:
        prompts.append(load_prompt_template(mode, prompts_dir=prompts_dir))
    return "\n\n".join(prompts)

def build_final_prompt(modes, diff, prompts_dir="prompts", max_diff_length=8000):
    """
    Combine prompt templates for the selected modes and inject the diff with clean formatting.
    Warn if the diff is overly large, but do not truncate by default.
    """
    prompt = combine_prompt_templates(modes, prompts_dir=prompts_dir)
    warning = ""
    if len(diff) > max_diff_length:
        warning = f"\n\n⚠️ Warning: Diff is very large ({len(diff)} chars). LLM may not process the full context."
    formatted = f"{prompt}\n\n---\n\n### Git Diff\n\n```diff\n{diff}\n```{warning}"
    return formatted

def call_llm(prompt, provider="openai", model=None, model_preference=("gpt-4-turbo", "gpt-3.5-turbo")):
    """
    Send the prompt to the selected LLM provider.
    provider: 'openai', 'google', 'anthropic', etc.
    model: model name to use (overrides default)
    Returns the parsed response or raises an error.
    """
    if provider == "openai":
        openai.api_key = get_openai_api_key()
        last_error = None
        models = [model] if model else list(model_preference)
        for m in models:
            try:
                response = openai.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=2048
                )
                content = response.choices[0].message.content
                # Basic validation: ensure response is not empty
                if not content.strip():
                    raise ValueError("LLM response is empty.")
                return content
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"All LLM model calls failed. Last error: {last_error}")
    elif provider == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found. Please set it in your .env file or environment variables.")
        # Use a valid Gemini model name as default
        model_name = model or "gemini-1.5-flash"
        # Remove leading 'models/' if present
        if model_name.startswith("models/"):
            model_name = model_name[len("models/"):]
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {"key": api_key}
        try:
            resp = requests.post(url, headers=headers, params=params, json=data, timeout=60)
            try:
                resp.raise_for_status()
            except requests.HTTPError as e:
                print("Gemini API error response:")
                print(resp.text)
                if resp.status_code == 404:
                    print("\nModel not found. Try using --model models/gemini-1.5-flash or check the Gemini API documentation for available models.")
                raise
            result = resp.json()
            content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not content.strip():
                raise ValueError("Gemini response is empty.")
            return content
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
    else:
        raise NotImplementedError(f"Provider '{provider}' is not supported yet.")
