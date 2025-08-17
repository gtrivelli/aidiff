"""Command-line interface for AIDiff."""

import argparse
import sys
from typing import List
from aidiff.core.models import ReviewConfig
from aidiff.core.reviewer import AIDiffReviewer
from aidiff.core.exceptions import AIDiffError


class AIDiffCLI:
    """Command-line interface for AIDiff."""

    def __init__(self):
        """Initialize CLI."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser."""
        parser = argparse.ArgumentParser(
            description="AIDiff: LLM-powered git diff reviewer",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--base', 
            type=str, 
            default='origin/main',
            help='Base branch to diff against (default: origin/main)'
        )
        
        parser.add_argument(
            '--staged', 
            action='store_true',
            help='Only include staged changes in the diff'
        )
        
        parser.add_argument(
            '--modes', 
            nargs='+', 
            default=['security'],
            help='Review modes: security, accessibility, performance'
        )
        
        parser.add_argument(
            '--include-untracked', 
            action='store_true',
            help='Include untracked files in the diff'
        )
        
        parser.add_argument(
            '--provider', 
            type=str, 
            default='chatgpt',
            choices=['chatgpt', 'gemini', 'claude'],
            help='LLM provider to use'
        )
        
        parser.add_argument(
            '--model', 
            type=str, 
            default=None,
            help='LLM model name (e.g. gpt-4-turbo, gemini-pro, claude-3-sonnet, etc)'
        )
        
        parser.add_argument(
            '--output', 
            type=str, 
            default='markdown',
            choices=['markdown', 'plain', 'json'],
            help='Output format: markdown, plain, or json'
        )
        
        parser.add_argument(
            '--dry-run', 
            action='store_true',
            help='Show prompt and diff, but do not call the LLM'
        )
        
        parser.add_argument(
            '--debug', 
            action='store_true',
            help='Print extra debug information'
        )
        
        parser.add_argument(
            '--prompts-dir', 
            type=str, 
            default='prompts',
            help='Directory containing prompt templates'
        )
        
        return parser

    def run(self, args: List[str] = None) -> int:
        """
        Run the CLI with provided arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            parsed_args = self.parser.parse_args(args)
            config = self._create_config(parsed_args)
            
            reviewer = AIDiffReviewer(config)
            result = reviewer.review()
            
            print(result)
            return 0
            
        except AIDiffError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    def _create_config(self, args: argparse.Namespace) -> ReviewConfig:
        """
        Create ReviewConfig from parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            ReviewConfig instance
        """
        return ReviewConfig(
            base_branch=args.base,
            modes=args.modes,
            provider=args.provider,
            model=args.model,
            output_format=args.output,
            staged=args.staged,
            include_untracked=args.include_untracked,
            dry_run=args.dry_run,
            debug=args.debug,
            prompts_dir=args.prompts_dir
        )


def main():
    """Main entry point for the CLI."""
    cli = AIDiffCLI()
    sys.exit(cli.run())
