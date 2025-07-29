"""Plain text output formatter."""

from typing import List
from aidiff.formatters import OutputFormatter
from aidiff.core.models import Issue


class PlainFormatter(OutputFormatter):
    """Formats issues as plain text."""

    def format_issues(self, issues: List[Issue], group_by: str = 'file') -> str:
        """
        Format issues as plain text.
        
        Args:
            issues: List of issues to format
            group_by: Field to group issues by (ignored in plain format)
            
        Returns:
            Formatted plain text string
        """
        output_lines = []
        
        for issue in issues:
            output_lines.append(f"Issue: {issue.issue}")
            output_lines.append(f"File: {issue.file}")
            output_lines.append(f"Line Number: {issue.line_number}")
            output_lines.append(f"Code: {issue.code}")
            output_lines.append(f"Severity: {issue.severity}")
            output_lines.append(f"Confidence: {issue.confidence}")
            output_lines.append(f"Suggestion: {issue.suggestion}")
            output_lines.append("")  # Empty line between issues
        
        return '\n'.join(output_lines)
