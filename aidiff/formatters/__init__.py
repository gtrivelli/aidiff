"""Output formatters module."""

from abc import ABC, abstractmethod
from typing import List
from aidiff.core.models import Issue


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format_issues(self, issues: List[Issue], group_by: str = 'file') -> str:
        """
        Format issues for output.
        
        Args:
            issues: List of issues to format
            group_by: Field to group issues by
            
        Returns:
            Formatted output string
        """
        pass
