"""Plain text output formatter."""

from typing import List
from aidiff.formatters import OutputFormatter
from aidiff.core.models import Issue


class PlainFormatter(OutputFormatter):
    """Formats issues as plain text."""

    def format_issues(self, issues: List[Issue], group_by: str = 'file') -> str:
        """
        Format issues as plain text compatible with frontend parser.
        
        Args:
            issues: List of issues to format
            group_by: Field to group issues by
            
        Returns:
            Formatted plain text string compatible with frontend parser
        """
        if not issues:
            return ""
            
        output_lines = []
        
        # Group issues by file
        grouped = {}
        for issue in issues:
            file_key = getattr(issue, group_by, 'Unknown')
            if file_key not in grouped:
                grouped[file_key] = []
            grouped[file_key].append(issue)
        
        # Format each group
        for file_name, file_issues in grouped.items():
            if file_name and file_name != 'N/A':
                output_lines.append(f"### `{file_name}`")
                output_lines.append("")
            
            for issue in file_issues:
                # Use security emoji for all issues (could be made dynamic based on mode)
                output_lines.append(f"🔒 **Issue:** {issue.issue}")
                if issue.severity:
                    output_lines.append(f"**Severity:** {issue.severity}")
                if issue.confidence:
                    output_lines.append(f"**Confidence:** {issue.confidence}")
                if issue.line_number and issue.line_number != 'N/A':
                    output_lines.append(f"**Line Number:** {issue.line_number}")
                if issue.code and issue.code != 'N/A':
                    output_lines.append(f"**Code:** {issue.code}")
                if issue.suggestion:
                    output_lines.append(f"**Suggestion:** {issue.suggestion}")
                if issue.file and issue.file != 'N/A':
                    output_lines.append(f"**File:** {issue.file}")
                # Add review type information for multi-mode analysis
                if hasattr(issue, 'review_type') and issue.review_type:
                    output_lines.append(f"**Review Type:** {issue.review_type}")
                output_lines.append("")  # Empty line between issues
        
        return '\n'.join(output_lines)
