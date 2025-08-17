"""Convert legacy issue format to DTO format."""

import re
from typing import List, Optional, Dict
from datetime import datetime
from aidiff.core.models import Issue
import sys
import os

# Add the backend directory to the path to import dto
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

try:
    from dto import IssueDTO, FileAnalysisDTO, AnalysisResultDTO, Severity, ReviewType
    from dto import parse_severity, parse_line_numbers, parse_confidence
except ImportError as e:
    # Fallback if DTO import fails - create simple classes
    class Severity:
        HIGH = "High"
        MEDIUM = "Medium"
        LOW = "Low"
    
    class ReviewType:
        SECURITY = "security"
        ACCESSIBILITY = "accessibility"
        PERFORMANCE = "performance"
        QUALITY = "quality"
    
    # Re-raise the import error for debugging
    raise ImportError(f"Failed to import DTO classes: {e}")


class DTOConverter:
    """Converts legacy Issue objects to DTO format."""

    @staticmethod
    def convert_issues_to_dto(issues: List[Issue], review_types: List[str]) -> 'AnalysisResultDTO':
        """
        Convert list of Issue objects to AnalysisResultDTO.
        
        Args:
            issues: List of Issue objects from the legacy parser
            review_types: List of review types that were analyzed
            
        Returns:
            AnalysisResultDTO object
        """
        if not issues:
            return AnalysisResultDTO(
                files=[],
                total_issues=0,
                analysis_timestamp=datetime.now().isoformat(),
                review_types=[ReviewType(rt) for rt in review_types if rt in [e.value for e in ReviewType]]
            )

        # Group issues by file
        files_dict: Dict[str, List['IssueDTO']] = {}
        
        for issue in issues:
            file_path = issue.file or "unknown_file"
            
            # Convert Issue to IssueDTO
            dto_issue = DTOConverter._convert_single_issue_to_dto(issue, review_types)
            dto_issue.file_path = file_path
            
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(dto_issue)

        # Create FileAnalysisDTO objects
        file_analyses = []
        for file_path, file_issues in files_dict.items():
            file_analysis = FileAnalysisDTO(
                file_path=file_path,
                issues=file_issues,
                review_types_analyzed=[ReviewType(rt) for rt in review_types if rt in [e.value for e in ReviewType]]
            )
            file_analyses.append(file_analysis)

        return AnalysisResultDTO(
            files=file_analyses,
            total_issues=len(issues),
            analysis_timestamp=datetime.now().isoformat(),
            review_types=[ReviewType(rt) for rt in review_types if rt in [e.value for e in ReviewType]]
        )

    @staticmethod
    def _convert_single_issue_to_dto(issue: Issue, review_types: List[str]) -> 'IssueDTO':
        """
        Convert a single Issue object to IssueDTO.
        
        Args:
            issue: Legacy Issue object
            review_types: Available review types to determine which type this issue belongs to
            
        Returns:
            IssueDTO object
        """
        # Parse severity
        severity = parse_severity(issue.severity or "medium")
        
        # Parse confidence
        confidence = parse_confidence(issue.confidence or "50%")
        
        # Parse line numbers
        line_numbers = parse_line_numbers(issue.line_number or "")
        
        # Determine review type based on issue content and available review types
        review_type = DTOConverter._determine_review_type(issue, review_types)
        
        return IssueDTO(
            issue=issue.issue or "Unknown issue",
            severity=severity,
            confidence=confidence,
            line_numbers=line_numbers,
            code=issue.code or "",
            suggestion=issue.suggestion or "No suggestion provided",
            review_type=review_type,
            file_path=None  # Will be set by the caller
        )

    @staticmethod
    def _determine_review_type(issue: Issue, review_types: List[str]) -> 'ReviewType':
        """
        Determine the review type for an issue based on its content and available review types.
        
        Args:
            issue: Issue object
            review_types: List of review types that were run
            
        Returns:
            ReviewType enum value
        """
        issue_text = (issue.issue or "").lower()
        
        # Keywords for each review type
        security_keywords = ["security", "vulnerability", "authentication", "authorization", "xss", 
                           "sql injection", "csrf", "hardcoded", "password", "token", "api key"]
        accessibility_keywords = ["accessibility", "aria", "alt text", "screen reader", "contrast", 
                                "keyboard", "focus", "wcag", "semantic"]
        performance_keywords = ["performance", "slow", "optimize", "memory", "cpu", "cache", 
                              "async", "blocking", "inefficient"]
        quality_keywords = ["quality", "code quality", "maintainability", "readability", "complexity",
                          "best practice", "refactor", "clean code"]
        
        # Check each review type in order of specificity
        if "security" in review_types and any(keyword in issue_text for keyword in security_keywords):
            return ReviewType.SECURITY
        elif "accessibility" in review_types and any(keyword in issue_text for keyword in accessibility_keywords):
            return ReviewType.ACCESSIBILITY  
        elif "performance" in review_types and any(keyword in issue_text for keyword in performance_keywords):
            return ReviewType.PERFORMANCE
        elif "quality" in review_types and any(keyword in issue_text for keyword in quality_keywords):
            return ReviewType.QUALITY
            
        # Fallback: return the first available review type
        if review_types:
            if "security" in review_types:
                return ReviewType.SECURITY
            elif "accessibility" in review_types:
                return ReviewType.ACCESSIBILITY
            elif "performance" in review_types:
                return ReviewType.PERFORMANCE
            elif "quality" in review_types:
                return ReviewType.QUALITY
                
        # Final fallback
        return ReviewType.SECURITY
