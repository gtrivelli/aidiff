# Entry point for AIDiff CLI

import argparse
import subprocess
from diff_parser import clean_diff
from reviewer import build_final_prompt
from utils import parse_llm_output, print_issues_markdown
from reviewer import call_llm
from result_processor import LLMResultProcessor
from dto import AnalysisResultDTO

def parse_args():
    parser = argparse.ArgumentParser(description="AIDiff: LLM-powered git diff reviewer")
    parser.add_argument('--base', type=str, default='origin/main', help='Base branch to diff against (default: origin/main)')
    parser.add_argument('--staged', action='store_true', help='Only include staged changes in the diff')
    parser.add_argument('--modes', nargs='+', default=['security'], help='Review modes: security, accessibility, performance, quality')
    parser.add_argument('--include-untracked', action='store_true', help='Include untracked files in the diff')
    parser.add_argument('--provider', type=str, default='chatgpt', choices=['chatgpt', 'gemini', 'claude', 'copilot'], help='LLM provider to use (chatgpt, gemini, claude, copilot)')
    parser.add_argument('--model', type=str, default=None, help='LLM model name (e.g. gpt-4-turbo, gemini-pro, etc)')
    parser.add_argument('--output', type=str, default='markdown', choices=['markdown', 'plain', 'json'], help='Output format: markdown, plain, or json')
    parser.add_argument('--dry-run', action='store_true', help='Show prompt and diff, but do not call the LLM')
    parser.add_argument('--debug', action='store_true', help='Print extra debug information (raw LLM response, API call details)')
    parser.add_argument('--chatgpt-api-key', type=str, help='ChatGPT (OpenAI) API Key (overrides environment variable)')
    parser.add_argument('--gemini-api-key', type=str, help='Gemini API Key (overrides environment variable)')
    parser.add_argument('--llm-result', type=str, help='Pre-computed LLM result from VS Code Copilot integration')
    return parser.parse_args()

def is_dirty_working_tree():
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    return bool(result.stdout.strip())

def get_git_diff(base_branch, staged=False):
    try:
        if staged:
            # For staged changes, don't use base_branch - just get what's staged
            diff_cmd = ['git', 'diff', '--staged']
        else:
            diff_cmd = ['git', 'diff', base_branch]
        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If base_branch doesn't exist, try different approaches
        print(f"Error with base branch '{base_branch}': {e}")
        
        # Try just getting unstaged changes
        try:
            result = subprocess.run(['git', 'diff'], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("Using unstaged changes")
                return result.stdout
        except subprocess.CalledProcessError:
            pass
        
        # Try HEAD if available
        try:
            result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("Using changes against HEAD")
                return result.stdout
        except subprocess.CalledProcessError:
            pass
        
        # Try cached changes
        try:
            result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("Using staged changes")
                return result.stdout
        except subprocess.CalledProcessError:
            pass
        
        print(f"No git diff available: {e}")
        return None

def get_untracked_files():
    result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], capture_output=True, text=True)
    return [f for f in result.stdout.splitlines() if f]

def get_untracked_file_diff(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        diff = f"diff --git a/{file_path} b/{file_path}\nnew file mode 100644\n--- /dev/null\n+++ b/{file_path}\n"
        for line in content.splitlines():
            diff += f"+{line}\n"
        return diff
    except Exception as e:
        return f"# Could not read untracked file {file_path}: {e}\n"

if __name__ == "__main__":
    args = parse_args()
    
    # Set environment variables from command line args if provided
    if args.chatgpt_api_key:
        import os
        os.environ['OPENAI_API_KEY'] = args.chatgpt_api_key
    if args.gemini_api_key:
        import os
        os.environ['GEMINI_API_KEY'] = args.gemini_api_key
    
    if is_dirty_working_tree():
        print("Warning: You have uncommitted changes in your working tree.")
    print(f"Base branch selected: {args.base}")
    print(f"Modes: {args.modes}")
    diff = get_git_diff(args.base, staged=args.staged) or ""
    if args.include_untracked:
        untracked_files = get_untracked_files()
        for file_path in untracked_files:
            diff += get_untracked_file_diff(file_path)
    if not diff.strip():
        print("No diff found or error occurred.")
        exit(1)
    cleaned_diff = clean_diff(diff)
    prompt = build_final_prompt(args.modes, cleaned_diff)
    if args.dry_run or args.debug:
        print("\n===== FINAL PROMPT TO SEND TO LLM =====\n")
        print(prompt)
        if args.dry_run:
            print("\n(Dry run: skipping LLM call)")
            exit(0)
    # --- LLM call and output formatting ---
    if args.llm_result:
        # Use pre-computed result from VS Code Copilot integration
        llm_response = args.llm_result
        print("Using Copilot analysis result from VS Code extension")
    else:
        # Call LLM directly using the provider name
        try:
            llm_response = call_llm(prompt, provider=args.provider, model=args.model) if not args.dry_run else ""
        except Exception as e:
            error_msg = str(e).lower()
            print(f"\n⚠️  LLM call failed: {e}")
            
            # Provide helpful error messages and fallback to dry-run
            if "503" in error_msg or "service unavailable" in error_msg:
                print(f"🔄 {args.provider.title()} servers are temporarily unavailable. This is usually temporary.")
                print("💡 You can try again in a few minutes, or switch to a different provider.")
            elif "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                print(f"📊 {args.provider.title()} API quota/rate limit exceeded.")
                print("💡 You can wait for the limit to reset, or switch to a different provider.")
            elif "unauthorized" in error_msg or "invalid api key" in error_msg:
                print(f"🔑 {args.provider.title()} API key is invalid or missing.")
                print("💡 Please check your API key configuration.")
            elif "timeout" in error_msg or "connection" in error_msg:
                print(f"🌐 Network timeout or connection error with {args.provider.title()}.")
                print("💡 Please check your internet connection and try again.")
            else:
                print(f"❌ Unexpected error with {args.provider.title()} provider.")
            
            print("\n🔄 Falling back to dry-run mode...\n")
            llm_response = ""
            args.dry_run = True
    
    if args.debug:
        print("\n===== RAW LLM RESPONSE =====\n")
        print(llm_response)
    
    # Get list of files analyzed
    analyzed_files = []
    if args.include_untracked:
        analyzed_files.extend(get_untracked_files())
    
    # Extract files from diff as well
    if diff.strip():
        import re
        file_pattern = r'^diff --git a\/(.+?) b\/(.+?)$'
        for match in re.finditer(file_pattern, diff, re.MULTILINE):
            analyzed_files.append(match.group(2))
    
    # Process results using new DTO system
    processor = LLMResultProcessor()
    result_dto = processor.process_llm_response(llm_response, args.modes, analyzed_files)
    
    if args.dry_run and not args.llm_result:
        # In dry-run mode, provide informative message but still output valid DTO structure
        if args.output == 'json':
            print(result_dto.to_json())
        else:
            print("No issues found (dry-run mode - LLM analysis was skipped).")
    elif result_dto.total_issues == 0:
        if args.output == 'json':
            print(result_dto.to_json())
        else:
            print("No issues found by LLM.")
    else:
        print(f"\n===== LLM REVIEW RESULTS ({result_dto.total_issues} issues found) =====\n")
        
        if args.output == 'json':
            # Output structured JSON for VS Code extension
            print(result_dto.to_json())
        elif args.output == 'markdown':
            # Output formatted markdown for human reading
            for file_analysis in result_dto.files:
                if file_analysis.issues:
                    print(f"### `{file_analysis.file_path}`\n")
                    for issue in file_analysis.issues:
                        print(f"**Issue:** {issue.issue}")
                        print(f"**File:** {issue.file_path}")
                        print(f"**Line Number(s):** {', '.join(map(str, issue.line_numbers))}")
                        print(f"**Code:** {issue.code}")
                        print(f"**Severity:** {issue.severity.value}")
                        print(f"**Confidence:** {issue.confidence}%")
                        print(f"**Suggestion:** {issue.suggestion}")
                        print(f"**Type:** {issue.review_type.value}")
                        print("---\n")
        else:
            # Plain text output
            for file_analysis in result_dto.files:
                for issue in file_analysis.issues:
                    print(f"Issue: {issue.issue}")
                    print(f"File: {issue.file_path}")
                    print(f"Line Number(s): {', '.join(map(str, issue.line_numbers))}")
                    print(f"Code: {issue.code}")
                    print(f"Severity: {issue.severity.value}")
                    print(f"Confidence: {issue.confidence}%")
                    print(f"Suggestion: {issue.suggestion}")
                    print(f"Type: {issue.review_type.value}")
                    print()
