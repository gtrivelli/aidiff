"""AIDiff: LLM-powered git diff reviewer."""

__version__ = "1.0.0"
__author__ = "AIDiff Contributors"

from aidiff.core.models import Issue, ReviewConfig
from aidiff.core.reviewer import AIDiffReviewer

__all__ = ["Issue", "ReviewConfig", "AIDiffReviewer"]
