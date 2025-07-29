"""Prompt management for AIDiff."""

import os
from typing import List
from aidiff.core.exceptions import PromptError


class PromptManager:
    """Manages prompt templates for different review modes."""

    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize with prompts directory."""
        self.prompts_dir = prompts_dir

    def load_prompt_template(self, mode: str) -> str:
        """
        Load a prompt template file from the prompts directory.
        
        Args:
            mode: Review mode (e.g. 'security', 'accessibility', 'performance')
            
        Returns:
            Content of the prompt template
            
        Raises:
            PromptError: If template file not found
        """
        filename = f"{mode}.md"
        path = os.path.join(self.prompts_dir, filename)
        
        if not os.path.exists(path):
            raise PromptError(f"Prompt template not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise PromptError(f"Error reading prompt template {path}: {e}")

    def combine_prompt_templates(self, modes: List[str]) -> str:
        """
        Combine multiple prompt templates for the selected modes.
        
        Args:
            modes: List of review modes
            
        Returns:
            Combined prompt templates separated by two newlines
        """
        prompts = []
        for mode in modes:
            prompts.append(self.load_prompt_template(mode))
        return "\n\n".join(prompts)

    def build_final_prompt(self, modes: List[str], diff: str, max_diff_length: int = 8000) -> str:
        """
        Combine prompt templates for the selected modes and inject the diff.
        
        Args:
            modes: Review modes to use
            diff: Git diff content
            max_diff_length: Maximum diff length before warning
            
        Returns:
            Final formatted prompt
        """
        prompt = self.combine_prompt_templates(modes)
        
        warning = ""
        if len(diff) > max_diff_length:
            warning = f"\n\n⚠️ Warning: Diff is very large ({len(diff)} chars). LLM may not process the full context."
        
        formatted = f"{prompt}\n\n---\n\n### Git Diff\n\n```diff\n{diff}\n```{warning}"
        return formatted
