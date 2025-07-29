"""Updated test suite for refactored AIDiff."""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

from aidiff.core.models import ReviewConfig, Issue
from aidiff.core.prompt_manager import PromptManager
from aidiff.core.diff_parser import DiffParser
from aidiff.utils.issue_parser import IssueParser
from aidiff.utils.issue_filter import IssueFilter
from aidiff.formatters.markdown_formatter import MarkdownFormatter
from aidiff.formatters.plain_formatter import PlainFormatter


class TestPromptManager(unittest.TestCase):
    """Test prompt management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory with test prompt
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_file = os.path.join(self.temp_dir, "security.md")
        with open(self.prompt_file, 'w') as f:
            f.write("Test security prompt")
        
        self.prompt_manager = PromptManager(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_prompt_template(self):
        """Test loading a prompt template."""
        content = self.prompt_manager.load_prompt_template("security")
        self.assertEqual(content, "Test security prompt")

    def test_build_final_prompt(self):
        """Test building final prompt with diff."""
        diff = '+print("hello")\n'
        prompt = self.prompt_manager.build_final_prompt(['security'], diff)
        self.assertIn('Git Diff', prompt)
        self.assertIn(diff.strip(), prompt)
        self.assertIn("Test security prompt", prompt)


class TestDiffParser(unittest.TestCase):
    """Test diff parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = DiffParser()

    def test_clean_diff(self):
        """Test diff cleaning."""
        raw = 'diff --git a/foo.py b/foo.py\nindex 123..456\n+print("hi")\n'
        cleaned = self.parser.clean_diff(raw)
        self.assertIn('+print("hi")', cleaned)
        self.assertIn('diff --git a/foo.py b/foo.py', cleaned)
        self.assertNotIn('index 123..456', cleaned)


class TestIssueParser(unittest.TestCase):
    """Test LLM output parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = IssueParser()

    def test_parse_llm_output(self):
        """Test parsing LLM output."""
        llm_output = '''---
**Issue:** Hardcoded secret
**File:** foo.py
**Severity:** High
**Confidence:** 95%
**Suggestion:** Remove secret
---'''
        issues = self.parser.parse_llm_output(llm_output)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].file, 'foo.py')
        self.assertIn('Hardcoded secret', issues[0].issue)
        self.assertEqual(issues[0].severity, 'High')

    def test_parse_empty_output(self):
        """Test parsing empty output."""
        issues = self.parser.parse_llm_output("")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].file, 'N/A')


class TestIssueFilter(unittest.TestCase):
    """Test issue filtering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.filter = IssueFilter()

    def test_filter_placeholder_values(self):
        """Test filtering issues with placeholder values."""
        issue = Issue(
            issue="API key found",
            file="config.py",
            code="API_KEY = 'your_api_key_here'",
            severity="high",
            confidence="90%",
            suggestion="Use environment variables"
        )
        
        filtered = self.filter.filter_false_positives([issue])
        self.assertEqual(len(filtered), 0)  # Should be filtered out

    def test_keep_real_issues(self):
        """Test keeping real issues."""
        issue = Issue(
            issue="Hardcoded password found",
            file="auth.py",
            code="password = 'secret123'",
            severity="critical",
            confidence="95%",
            suggestion="Use secure password storage"
        )
        
        filtered = self.filter.filter_false_positives([issue])
        self.assertEqual(len(filtered), 1)  # Should be kept


class TestFormatters(unittest.TestCase):
    """Test output formatters."""

    def setUp(self):
        """Set up test fixtures."""
        self.issue = Issue(
            issue="Test issue",
            file="test.py",
            severity="high",
            confidence="90%",
            suggestion="Fix this",
            line_number="10",
            code="test code"
        )

    def test_markdown_formatter(self):
        """Test markdown formatting."""
        formatter = MarkdownFormatter()
        output = formatter.format_issues([self.issue])
        self.assertIn("### `test.py`", output)
        self.assertIn("**Issue:** Test issue", output)
        self.assertIn("⚠️", output)  # High severity emoji

    def test_plain_formatter(self):
        """Test plain text formatting."""
        formatter = PlainFormatter()
        output = formatter.format_issues([self.issue])
        self.assertIn("Issue: Test issue", output)
        self.assertIn("File: test.py", output)


class TestReviewConfig(unittest.TestCase):
    """Test review configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ReviewConfig()
        self.assertEqual(config.base_branch, "origin/main")
        self.assertEqual(config.modes, ["security"])
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.output_format, "markdown")
        self.assertFalse(config.dry_run)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ReviewConfig(
            base_branch="main",
            modes=["security", "performance"],
            provider="google",
            dry_run=True
        )
        self.assertEqual(config.base_branch, "main")
        self.assertEqual(config.modes, ["security", "performance"])
        self.assertEqual(config.provider, "google")
        self.assertTrue(config.dry_run)


if __name__ == '__main__':
    unittest.main()
