"""
Result processor to convert LLM output to structured DTOs
"""
import re
from typing import List, Dict
from datetime import datetime
from dto import (
    IssueDTO, FileAnalysisDTO, AnalysisResultDTO, 
    ReviewType, parse_severity, parse_line_numbers, parse_confidence
)

class LLMResultProcessor:
    """Processes raw LLM output into structured DTOs"""
    
    def __init__(self):
        self.current_file = None
        
    def process_llm_response(self, llm_response: str, review_types: List[str], files_analyzed: List[str]) -> AnalysisResultDTO:
        """
        Convert raw LLM response text to structured AnalysisResultDTO
        s
        Args:
            llm_response: Raw text response from LLM
            review_types: List of review types that were analyzed
            files_analyzed: List of file paths that were analyzed
            
        Returns:
            AnalysisResultDTO with structured results
        """
        # Parse issues from the LLM response
        issues = self._parse_issues_from_response(llm_response, review_types)
        
        # Group issues by file
        files_dict = {}
        for file_path in files_analyzed:
            files_dict[file_path] = []
            
        # Assign issues to files
        for issue in issues:
            if issue.file_path and issue.file_path in files_dict:
                files_dict[issue.file_path].append(issue)
            else:
                # Try to find the best matching file if file_path is not exact
                matched_file = self._find_matching_file(issue.file_path, files_analyzed)
                if matched_file:
                    issue.file_path = matched_file
                    files_dict[matched_file].append(issue)
        
        # Create FileAnalysisDTO objects
        file_analyses = []
        review_type_enums = [ReviewType(rt) for rt in review_types]
        
        for file_path, file_issues in files_dict.items():
            file_analysis = FileAnalysisDTO(
                file_path=file_path,
                issues=file_issues,
                review_types_analyzed=review_type_enums
            )
            file_analyses.append(file_analysis)
        
        # Create final result
        total_issues = sum(len(fa.issues) for fa in file_analyses)
        
        return AnalysisResultDTO(
            files=file_analyses,
            total_issues=total_issues,
            analysis_timestamp=datetime.now().isoformat(),
            review_types=review_type_enums
        )
    
    def _parse_issues_from_response(self, response: str, review_types: List[str]) -> List[IssueDTO]:
        """Parse individual issues from LLM response text"""
        issues = []
        
        # Clean up the response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```markdown'):
            response = response[11:]  # Remove ```markdown
        if response.startswith('```'):
            response = response[3:]   # Remove ```
        if response.endswith('```'):
            response = response[:-3]  # Remove trailing ```
        
        # Split response into potential issue blocks using separators
        # Look for --- separators or **Issue:** patterns
        issue_blocks = []
        
        # First try splitting by --- separators
        parts = response.split('---')
        for part in parts:
            part = part.strip()
            if part and ('**Issue:**' in part or '**File:**' in part):
                issue_blocks.append(part)
        
        # If no --- separators found, try splitting by **Issue:** pattern
        if not issue_blocks:
            issue_pattern = r'(?=\*\*Issue:\*\*)'
            issue_blocks = re.split(issue_pattern, response, flags=re.MULTILINE | re.IGNORECASE)
            issue_blocks = [block.strip() for block in issue_blocks if block.strip()]
        
        current_file = None
        
        for block in issue_blocks:
            if not block.strip():
                continue
                
            # Check if this block contains a file header
            file_match = re.search(r'###\s*`([^`]+)`', block)
            if file_match:
                current_file = file_match.group(1)
                continue
            
            # Try to parse this block as an issue
            issue = self._parse_single_issue(block, review_types, current_file)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _parse_single_issue(self, block: str, review_types: List[str], current_file: str = None) -> IssueDTO:
        """Parse a single issue from a text block"""
        try:
            # Extract fields using regex patterns
            fields = {}
            
            # Issue description
            issue_match = re.search(r'\*\*Issue:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if issue_match:
                fields['issue'] = issue_match.group(1).strip()
            
            # File path
            file_match = re.search(r'\*\*File:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if file_match:
                fields['file'] = file_match.group(1).strip()
            elif current_file:
                fields['file'] = current_file
            
            # Line number(s)
            line_match = re.search(r'\*\*Line Number.*?:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if line_match:
                fields['line_number'] = line_match.group(1).strip()
            
            # Code
            code_match = re.search(r'\*\*Code:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if code_match:
                fields['code'] = code_match.group(1).strip()
            
            # Severity
            severity_match = re.search(r'\*\*Severity:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if severity_match:
                fields['severity'] = severity_match.group(1).strip()
            
            # Confidence
            confidence_match = re.search(r'\*\*Confidence:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if confidence_match:
                fields['confidence'] = confidence_match.group(1).strip()
            
            # Suggestion
            suggestion_match = re.search(r'\*\*Suggestion:\*\*\s*(.+?)(?=\n\*\*|\n---|$)', block, re.DOTALL)
            if suggestion_match:
                fields['suggestion'] = suggestion_match.group(1).strip()
            
            # Must have at least issue description to be valid
            if 'issue' not in fields:
                return None
            
            # Determine review type (default to first one if not specified)
            review_type = review_types[0] if review_types else 'security'
            for rt in review_types:
                if rt.lower() in block.lower():
                    review_type = rt
                    break
            
            # Create IssueDTO
            return IssueDTO(
                issue=fields.get('issue', 'Unknown issue'),
                severity=parse_severity(fields.get('severity', 'Medium')),
                confidence=parse_confidence(fields.get('confidence', '50%')),
                line_numbers=parse_line_numbers(fields.get('line_number', '')),
                code=fields.get('code', ''),
                suggestion=fields.get('suggestion', 'No suggestion provided'),
                review_type=ReviewType(review_type),
                file_path=fields.get('file')
            )
            
        except Exception as e:
            print(f"Error parsing issue block: {e}")
            return None
    
    def _find_matching_file(self, issue_file: str, available_files: List[str]) -> str:
        """Find the best matching file from available files"""
        if not issue_file:
            return None
            
        # Exact match
        if issue_file in available_files:
            return issue_file
        
        # Partial match (e.g., issue says "app.js" but file is "src/app.js")
        issue_basename = issue_file.split('/')[-1]
        for file_path in available_files:
            if file_path.endswith('/' + issue_basename) or file_path == issue_basename:
                return file_path
        
        # Return first file if no match (fallback)
        return available_files[0] if available_files else None
