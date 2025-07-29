"""Markdown output formatter."""

from typing import List
from collections import defaultdict
from aidiff.formatters import OutputFormatter
from aidiff.core.models import Issue


class MarkdownFormatter(OutputFormatter):
    """Formats issues as Markdown with emoji indicators."""

    def __init__(self):
        """Initialize formatter with emoji mapping."""
        self.emoji_map = {
            'critical': '🔒',
            'high': '⚠️',
            'medium': '⚠️',
            'low': '✅'
        }

    def format_issues(self, issues: List[Issue], group_by: str = 'file') -> str:
        """
        Format issues in CLI-friendly Markdown.
        
        Args:
            issues: List of issues to format
            group_by: Field to group issues by
            
        Returns:
            Formatted Markdown string
        """
        grouped = defaultdict(list)
        
        for issue in issues:
            key = getattr(issue, group_by, 'Unknown')
            grouped[key].append(issue)
        
        output_lines = []
        
        for group, group_issues in grouped.items():
            output_lines.append(f"\n### `{group}`\n")
            
            for issue in group_issues:
                severity = issue.severity.lower() if issue.severity else ''
                emoji = self.emoji_map.get(severity, '❓')
                
                output_lines.append(f"{emoji} **Issue:** {issue.issue}")
                output_lines.append(f"   **Severity:** {issue.severity}")
                output_lines.append(f"   **Confidence:** {issue.confidence}")
                
                if issue.line_number:
                    output_lines.append(f"   **Line Number:** {issue.line_number}")
                
                if issue.code:
                    output_lines.append(f"   **Code:** {issue.code}")
                
                output_lines.append(f"   **Suggestion:** {issue.suggestion}\n")
        
        return '\n'.join(output_lines)
