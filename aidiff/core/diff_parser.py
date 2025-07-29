"""Diff parsing utilities."""

from typing import List


class DiffParser:
    """Handles parsing and cleaning of git diff output."""

    @staticmethod
    def preserve_full_diff_format(diff_text: str) -> str:
        """
        Preserve the full Git diff output format, including file boundary markers.
        This function returns the diff unchanged to ensure all structure is kept.
        """
        return diff_text

    @staticmethod
    def clean_diff(diff_text: str) -> str:
        """
        Strip irrelevant metadata from a git diff, but keep file boundaries, 
        hunk headers, and diff lines.
        """
        cleaned = []
        for line in diff_text.splitlines():
            if line.startswith('diff --git a/'):
                cleaned.append(line)
            elif line.startswith('@@'):
                cleaned.append(line)
            elif line.startswith('+') or line.startswith('-') or line.startswith(' '):
                cleaned.append(line)
            # Ignore lines like 'index ...', 'new file mode ...', etc.
        return '\n'.join(cleaned)
