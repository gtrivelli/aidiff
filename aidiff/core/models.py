"""Data models for AIDiff."""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewMode(Enum):
    """Available review modes."""
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    QUALITY = "quality"


class LLMProvider(Enum):
    """Supported LLM providers."""
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    CLAUDE = "claude"


class OutputFormat(Enum):
    """Output formats."""
    MARKDOWN = "markdown"
    PLAIN = "plain"


@dataclass
class Issue:
    """Represents a code review issue."""
    issue: str
    file: str
    severity: str = ""
    confidence: str = ""
    suggestion: str = ""
    line_number: str = ""
    code: str = ""

    def __post_init__(self):
        """Ensure all fields are strings."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value is None:
                setattr(self, field_name, "")


@dataclass
class ReviewConfig:
    """Configuration for a review session."""
    base_branch: str = "origin/main"
    modes: List[str] = None
    provider: str = "chatgpt"
    model: Optional[str] = None
    output_format: str = "markdown"
    staged: bool = False
    include_untracked: bool = False
    dry_run: bool = False
    debug: bool = False
    max_diff_length: int = 8000
    prompts_dir: str = "prompts"

    def __post_init__(self):
        """Set default modes if none provided."""
        if self.modes is None:
            self.modes = ["security"]
