# Entry point for AutoDiff CLI

import argparse
import subprocess
from diff_parser import clean_diff
from reviewer import build_final_prompt
from utils import parse_llm_output, print_issues_markdown
from reviewer import call_llm

def parse_args():
    parser = argparse.ArgumentParser(description="AutoDiff: LLM-powered git diff reviewer")
    parser.add_argument('--base', type=str, default='origin/main', help='Base branch to diff against (default: origin/main)')
    parser.add_argument('--staged', action='store_true', help='Only include staged changes in the diff')
    parser.add_argument('--modes', nargs='+', default=['security'], help='Review modes: security, accessibility, performance')
    parser.add_argument('--include-untracked', action='store_true', help='Include untracked files in the diff')
    parser.add_argument('--provider', type=str, default='openai', choices=['openai', 'google', 'anthropic'], help='LLM provider to use (openai, google, anthropic, etc)')
    parser.add_argument('--model', type=str, default=None, help='LLM model name (e.g. gpt-4-turbo, gemini-pro, etc)')
    parser.add_argument('--output', type=str, default='markdown', choices=['markdown', 'plain'], help='Output format: markdown or plain')
    parser.add_argument('--dry-run', action='store_true', help='Show prompt and diff, but do not call the LLM')
    parser.add_argument('--debug', action='store_true', help='Print extra debug information (raw LLM response, API call details)')
    return parser.parse_args()

def is_dirty_working_tree():
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    return bool(result.stdout.strip())

def get_git_diff(base_branch, staged=False):
    try:
        if staged:
            diff_cmd = ['git', 'diff', '--cached', base_branch]
        else:
            diff_cmd = ['git', 'diff', base_branch]
        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
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
    llm_response = call_llm(prompt, provider=args.provider, model=args.model) if not args.dry_run else ""
    if args.debug:
        print("\n===== RAW LLM RESPONSE =====\n")
        print(llm_response)
    issues = parse_llm_output(llm_response)
    if not issues:
        print("No issues found by LLM.")
    else:
        print("\n===== LLM REVIEW RESULTS =====\n")
        if args.output == 'markdown':
            print_issues_markdown(issues)
        else:
            for issue in issues:
                print(f"Issue: {issue.get('issue','')}")
                print(f"File: {issue.get('file','')}")
                print(f"Line Number: {issue.get('line_number','')}")
                print(f"Code: {issue.get('code','')}")
                print(f"Severity: {issue.get('severity','')}")
                print(f"Confidence: {issue.get('confidence','')}")
                print(f"Suggestion: {issue.get('suggestion','')}")
                print()
