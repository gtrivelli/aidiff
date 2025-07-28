"""
Data Transfer Objects (DTOs) for AutoDiff analysis results
"""
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum
import json

class Severity(Enum):
    """Issue severity levels"""
    HIGH = "High"
    MEDIUM = "Medium" 
    LOW = "Low"

class ReviewType(Enum):
    """Types of reviews that can be performed"""
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"

@dataclass
class IssueDTO:
    """
    Data Transfer Object for a single issue found during review
    """
    issue: str                          # Description of the issue
    severity: Severity                  # High, Medium, Low
    confidence: int                     # Percentage (0-100)
    line_numbers: List[int]            # Line number(s) where issue occurs
    code: str                          # The actual code with the issue
    suggestion: str                    # How to fix the issue
    review_type: ReviewType            # Which review type found this issue
    file_path: Optional[str] = None    # File path (can be set separately)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "issue": self.issue,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "line_numbers": self.line_numbers,
            "code": self.code,
            "suggestion": self.suggestion,
            "review_type": self.review_type.value,
            "file_path": self.file_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'IssueDTO':
        """Create IssueDTO from dictionary"""
        return cls(
            issue=data["issue"],
            severity=Severity(data["severity"]),
            confidence=data["confidence"],
            line_numbers=data["line_numbers"],
            code=data["code"],
            suggestion=data["suggestion"],
            review_type=ReviewType(data["review_type"]),
            file_path=data.get("file_path")
        )

@dataclass
class FileAnalysisDTO:
    """
    Data Transfer Object for analysis results of a single file
    """
    file_path: str
    issues: List[IssueDTO]
    review_types_analyzed: List[ReviewType]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_path": self.file_path,
            "issues": [issue.to_dict() for issue in self.issues],
            "review_types_analyzed": [rt.value for rt in self.review_types_analyzed]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FileAnalysisDTO':
        """Create FileAnalysisDTO from dictionary"""
        return cls(
            file_path=data["file_path"],
            issues=[IssueDTO.from_dict(issue_data) for issue_data in data["issues"]],
            review_types_analyzed=[ReviewType(rt) for rt in data["review_types_analyzed"]]
        )

@dataclass
class AnalysisResultDTO:
    """
    Data Transfer Object for complete analysis results
    """
    files: List[FileAnalysisDTO]
    total_issues: int
    analysis_timestamp: str
    review_types: List[ReviewType]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "files": [file_analysis.to_dict() for file_analysis in self.files],
            "total_issues": self.total_issues,
            "analysis_timestamp": self.analysis_timestamp,
            "review_types": [rt.value for rt in self.review_types]
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'AnalysisResultDTO':
        """Create AnalysisResultDTO from dictionary"""
        return cls(
            files=[FileAnalysisDTO.from_dict(file_data) for file_data in data["files"]],
            total_issues=data["total_issues"],
            analysis_timestamp=data["analysis_timestamp"],
            review_types=[ReviewType(rt) for rt in data["review_types"]]
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisResultDTO':
        """Create AnalysisResultDTO from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

def parse_severity(severity_str: str) -> Severity:
    """Parse severity string to Severity enum, with fallback"""
    severity_str = severity_str.lower().strip()
    
    if severity_str in ['critical', 'high']:
        return Severity.HIGH
    elif severity_str in ['medium', 'moderate']:
        return Severity.MEDIUM
    elif severity_str in ['low', 'minor']:
        return Severity.LOW
    else:
        # Default to medium if unknown
        return Severity.MEDIUM

def parse_line_numbers(line_str: str) -> List[int]:
    """Parse line number string to list of integers"""
    if not line_str or line_str.strip() == '':
        return []
    
    try:
        # Handle various formats: "10", "10-12", "10,15,20", etc.
        line_str = line_str.strip()
        
        # Handle ranges like "10-12"
        if '-' in line_str and not line_str.startswith('-'):
            parts = line_str.split('-')
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                return list(range(start, end + 1))
        
        # Handle comma-separated like "10,15,20"
        if ',' in line_str:
            return [int(x.strip()) for x in line_str.split(',') if x.strip().isdigit()]
        
        # Single number
        if line_str.isdigit():
            return [int(line_str)]
            
        return []
    except (ValueError, TypeError):
        return []

def parse_confidence(confidence_str: str) -> int:
    """Parse confidence string to integer percentage"""
    if not confidence_str:
        return 50  # Default confidence
    
    try:
        # Remove % sign and any whitespace
        clean_str = confidence_str.replace('%', '').strip()
        confidence = int(clean_str)
        # Clamp to 0-100 range
        return max(0, min(100, confidence))
    except (ValueError, TypeError):
        return 50  # Default confidence
