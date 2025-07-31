"""Issue filtering utility."""

import re
from typing import List
from aidiff.core.models import Issue


class IssueFilter:
    """Filters out false positive issues."""

    def __init__(self):
        """Initialize filter with generic field names to exclude."""
        self.generic_fields = {
            'suggestion', 'issue', 'severity', 'confidence', 
            'file', 'code', 'line number'
        }

    def filter_false_positives(self, issues: List[Issue]) -> List[Issue]:
        """
        Remove issues that are false positives.
        
        Args:
            issues: List of issues to filter
            
        Returns:
            Filtered list of issues
        """
        # Read .gitignore to check for .env
        gitignore_content = self._read_gitignore()
        
        filtered = []
        
        for issue in issues:
            if self._is_false_positive(issue, gitignore_content):
                continue
            
            if not self._is_real_issue(issue):
                continue
                
            filtered.append(issue)
        
        return filtered

    def _read_gitignore(self) -> str:
        """Read .gitignore file content."""
        try:
            with open('.gitignore', 'r') as f:
                return f.read()
        except Exception:
            return ''

    def _is_placeholder_value(self, value: str) -> bool:
        """
        Check if value is a generic placeholder, not a real secret.
        
        Args:
            value: Value to check
            
        Returns:
            True if value appears to be a placeholder
        """
        if not value:
            return False
        
        value = value.strip().lower()
        
        # Common placeholder patterns
        if (
            'your' in value and 'key' in value
            or 'example' in value
            or value.startswith('<') and value.endswith('>')
            or 'changeme' in value
            or 'placeholder' in value
            or re.match(r'^[a-z_]*key[a-z_]*$', value)
        ):
            return True
        
        # Template variable pattern
        if re.match(r'<.*>', value):
            return True
        
        return False

    def _is_false_positive(self, issue: Issue, gitignore_content: str) -> bool:
        """
        Check if issue is a false positive.
        
        Args:
            issue: Issue to check
            gitignore_content: Content of .gitignore file
            
        Returns:
            True if issue is a false positive
        """
        # Check for placeholder values in relevant fields
        for field in ['code', 'suggestion', 'issue']:
            val = getattr(issue, field, '')
            if self._is_placeholder_value(val):
                return True
        
        # Check .env/.gitignore false positive
        if (
            issue.file.strip() == '.gitignore' and
            'not added to' in issue.issue.lower() and
            '.env' in gitignore_content
        ):
            return True
        
        return False

    def _is_real_issue(self, issue: Issue) -> bool:
        """
        Check if issue contains real content.
        
        Args:
            issue: Issue to check
            
        Returns:
            True if issue has substantial content
        """
        # Must have at least one important field with content
        important_fields = ['issue', 'suggestion', 'severity', 'confidence']
        if not any(getattr(issue, f, '').strip() for f in important_fields):
            return False
        
        # Skip if 'issue' field is exactly a generic field label or empty
        issue_val = issue.issue.strip().lower()
        if issue_val in self.generic_fields or not issue_val or re.fullmatch(r'^[\W_]+$', issue_val):
            return False
        
        # Clean up empty code field
        if not issue.code.strip():
            issue.code = ''
        
        return True
