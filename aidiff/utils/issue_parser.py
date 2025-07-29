"""Issue parsing utility."""

import re
from typing import List, Dict, Any
from aidiff.core.models import Issue


class IssueParser:
    """Parses LLM output into structured Issue objects."""

    def __init__(self):
        """Initialize parser with field mappings."""
        self.field_map = {
            'File': 'file',
            'Issue': 'issue',
            'Severity': 'severity',
            'Confidence': 'confidence',
            'Suggestion': 'suggestion',
            'Line Number': 'line_number',
            'Code': 'code',
        }

    def parse_llm_output(self, output: str) -> List[Issue]:
        """
        Parse LLM output and identify each issue block.
        
        Args:
            output: Raw LLM response text
            
        Returns:
            List of Issue objects
        """
        issues = []
        issue_blocks = re.split(r'---+', output)
        
        for block in issue_blocks:
            block = block.strip()
            if not block:
                continue
            
            issue_data = self._parse_issue_block(block)
            if issue_data:
                issues.append(Issue(**issue_data))
        
        # If no issues found, treat whole output as single issue
        if not issues:
            issues = [Issue(
                issue=output.strip(),
                file='N/A',
                severity='',
                confidence='',
                suggestion='',
                line_number='N/A',
                code='N/A'
            )]
        
        return issues

    def _parse_issue_block(self, block: str) -> Dict[str, Any]:
        """
        Parse a single issue block into a dictionary.
        
        Args:
            block: Text block containing issue information
            
        Returns:
            Dictionary with issue data
        """
        issue_data = {}
        lines = block.splitlines()
        field = None
        value_lines = []
        in_code_block = False
        code_block_delim = None

        for line in lines:
            line_stripped = line.strip()
            
            # Check for markdown field prefix
            matched_field = None
            for markdown_field in self.field_map.keys():
                prefix = f"**{markdown_field}:**"
                if line_stripped.startswith(prefix) and not in_code_block:
                    matched_field = markdown_field
                    break

            if matched_field:
                # Save previous field
                if field and value_lines:
                    val = self._process_field_value(value_lines, field, code_block_delim)
                    issue_data[self.field_map.get(field, field.lower().replace(' ', '_'))] = val

                field = matched_field
                val = line_stripped[len(f"**{matched_field}:**"):].lstrip()
                
                # Detect code block delimiter
                if field == 'Code' and (val.startswith('```') or val.startswith('``')):
                    in_code_block = True
                    code_block_delim = val[:3] if val.startswith('```') else val[:2]
                    value_lines = [val]
                else:
                    in_code_block = False
                    code_block_delim = None
                    value_lines = [val] if val else []
            else:
                if field == 'Code' and (in_code_block or line_stripped.startswith(('```', '``'))):
                    value_lines.append(line)
                    # End code block if delimiter found
                    if code_block_delim and line_stripped.startswith(code_block_delim):
                        in_code_block = False
                elif field:
                    value_lines.append(line)

        # Save last field
        if field and value_lines:
            val = self._process_field_value(value_lines, field, code_block_delim)
            issue_data[self.field_map.get(field, field.lower().replace(' ', '_'))] = val

        return issue_data

    def _process_field_value(self, value_lines: List[str], field: str, code_block_delim: str) -> str:
        """
        Process field value lines into final string value.
        
        Args:
            value_lines: Lines of text for the field
            field: Field name
            code_block_delim: Code block delimiter if applicable
            
        Returns:
            Processed field value
        """
        val = '\n'.join(value_lines).strip()
        
        if field == 'Code' and code_block_delim:
            # Remove code block delimiters
            val = re.sub(rf'^{re.escape(code_block_delim)}[a-zA-Z0-9]*', '', val)
            val = re.sub(rf'{re.escape(code_block_delim)}$', '', val).strip()
        
        return val
