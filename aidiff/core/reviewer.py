"""Main reviewer class that orchestrates the review process."""

from typing import List, Optional
from aidiff.core.models import Issue, ReviewConfig
from aidiff.core.git_ops import GitOperations
from aidiff.core.diff_parser import DiffParser
from aidiff.core.prompt_manager import PromptManager
from aidiff.providers.factory import LLMProviderFactory
from aidiff.formatters.factory import FormatterFactory
from aidiff.utils.config_loader import ConfigLoader
from aidiff.utils.issue_parser import IssueParser
from aidiff.utils.issue_filter import IssueFilter
from aidiff.utils.dto_converter import DTOConverter
from aidiff.core.exceptions import AIDiffError, GitError


class AIDiffReviewer:
    """Main class that orchestrates the AI diff review process."""

    def __init__(self, config: ReviewConfig):
        """
        Initialize reviewer with configuration.
        
        Args:
            config: Review configuration
        """
        self.config = config
        self.git_ops = GitOperations()
        self.diff_parser = DiffParser()
        self.prompt_manager = PromptManager(config.prompts_dir)
        self.config_loader = ConfigLoader()
        self.issue_parser = IssueParser()
        self.issue_filter = IssueFilter()

    def review(self) -> str:
        """
        Perform the complete review process.
        
        Returns:
            Formatted review output
            
        Raises:
            AIDiffError: If any step of the review process fails
        """
        try:
            # Step 1: Check git status and warn about dirty tree
            if self.git_ops.is_dirty_working_tree():
                print("Warning: You have uncommitted changes in your working tree.")

            print(f"Base branch selected: {self.config.base_branch}")
            print(f"Modes: {self.config.modes}")

            # Step 2: Get git diff
            diff = self._get_complete_diff()
            
            if not diff.strip():
                return "No diff found or error occurred."

            # Step 3: Clean and prepare diff
            cleaned_diff = self.diff_parser.clean_diff(diff)

            # Step 4: Build prompt
            prompt = self.prompt_manager.build_final_prompt(
                self.config.modes, 
                cleaned_diff, 
                self.config.max_diff_length
            )

            # Step 5: Handle dry run or debug output
            if self.config.dry_run or self.config.debug:
                print("\n===== FINAL PROMPT TO SEND TO LLM =====\n")
                print(prompt)
                if self.config.dry_run:
                    return "\n(Dry run: skipping LLM call)"

            # Step 6: Call LLM
            llm_response = self._call_llm(prompt)

            # Step 7: Debug output if requested
            if self.config.debug:
                print("\n===== RAW LLM RESPONSE =====\n")
                print(llm_response)

            # Step 8: Parse and filter issues
            issues = self.issue_parser.parse_llm_output(llm_response)
            filtered_issues = self.issue_filter.filter_false_positives(issues)

            # Step 9: Format output
            if not filtered_issues:
                if self.config.output_format == "json":
                    # Return empty DTO structure for JSON format
                    empty_dto = DTOConverter.convert_issues_to_dto([], self.config.modes)
                    return empty_dto.to_json()
                else:
                    return "No issues found by LLM."

            # Check if JSON output is requested
            if self.config.output_format == "json":
                # Convert issues to DTO and return as JSON
                analysis_result = DTOConverter.convert_issues_to_dto(filtered_issues, self.config.modes)
                return analysis_result.to_json()
            else:
                # Use legacy formatter for plain/markdown output
                formatter = FormatterFactory.create_formatter(self.config.output_format)
                formatted_output = "\n===== LLM REVIEW RESULTS =====\n\n" + formatter.format_issues(filtered_issues)
                return formatted_output

        except Exception as e:
            if isinstance(e, AIDiffError):
                raise
            else:
                raise AIDiffError(f"Unexpected error during review: {e}")

    def _get_complete_diff(self) -> str:
        """
        Get complete diff including untracked files if requested.
        
        Returns:
            Complete diff content
            
        Raises:
            GitError: If git operations fail
        """
        diff = self.git_ops.get_git_diff(self.config.base_branch, self.config.staged) or ""
        
        if self.config.include_untracked:
            untracked_files = self.git_ops.get_untracked_files()
            for file_path in untracked_files:
                diff += self.git_ops.get_untracked_file_diff(file_path)
        
        return diff

    def _call_llm(self, prompt: str) -> str:
        """
        Call the configured LLM provider.
        
        Args:
            prompt: Formatted prompt to send
            
        Returns:
            LLM response text
        """
        api_key = self.config_loader.get_api_key_for_provider(self.config.provider)
        provider = LLMProviderFactory.create_provider(self.config.provider, api_key)
        return provider.generate_response(prompt, self.config.model)
