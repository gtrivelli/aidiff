"""Custom exceptions for AIDiff."""


class AIDiffError(Exception):
    """Base exception for AIDiff."""
    pass


class GitError(AIDiffError):
    """Git-related errors."""
    pass


class PromptError(AIDiffError):
    """Prompt template related errors."""
    pass


class LLMError(AIDiffError):
    """LLM provider related errors."""
    pass


class ConfigError(AIDiffError):
    """Configuration related errors."""
    pass
