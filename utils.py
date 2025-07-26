# Utility functions for AIDiff

import re

def parse_llm_output(output):
    """
    Parse the LLM output and identify each issue block (file, severity, confidence, suggestion).
    Returns a list of dicts, one per issue.
    Handles both markdown and prose output from LLMs like Gemini.
    Enhanced to handle Gemini's prose/numbered-list style.
    """
    issues = []
    # Try to extract markdown-style blocks first
    issue_blocks = re.split(r'---+', output)
    for block in issue_blocks:
        if not block.strip():
            continue  # Skip empty blocks
        issue = {}
        file_match = re.search(r'\*\*File:\*\*\s*([^\n]+)', block)
        if file_match:
            issue['file'] = file_match.group(1).strip()
        else:
            file_match = re.search(r'`([^`]+)`', block)
            if file_match:
                issue['file'] = file_match.group(1)
        for field in ['Issue', 'Severity', 'Confidence', 'Suggestion', 'Line Number', 'Code']:
            match = re.search(rf'\*\*{field}:\*\*\s*(.+)', block)
            if match:
                issue[field.lower().replace(' ', '_')] = match.group(1).strip()
        # Ensure 'file', 'line_number', and 'code' are always present and meaningful
        if not issue.get('file') or issue['file'] == 'N/A':
            # Try to infer file from the diff context in the prompt (not just the block)
            file_match = re.search(r'diff --git a/([^\s]+)', output)
            if file_match:
                issue['file'] = file_match.group(1)
            else:
                issue['file'] = 'N/A'
        if 'line_number' not in issue or not issue['line_number'] or issue['line_number'] == 'N/A':
            # Try to infer line number from the code context in the block
            code_match = re.search(r'^\+[^+][^\n]+', block, re.MULTILINE)
            if code_match:
                # Try to find the line number in the diff hunk header
                hunk_match = re.search(r'^@@ -\d+(,\d+)? \+(\d+)', output, re.MULTILINE)
                if hunk_match:
                    issue['line_number'] = hunk_match.group(2)
                else:
                    issue['line_number'] = 'N/A'
            else:
                issue['line_number'] = 'N/A'
        if 'code' not in issue or not issue['code'] or issue['code'] == 'N/A':
            # Try to extract a code line from the diff block if possible
            code_match = re.search(r'^\+[^+][^\n]+', block, re.MULTILINE)
            if code_match:
                issue['code'] = code_match.group(0)
            else:
                issue['code'] = 'N/A'
        if issue:
            issues.append(issue)
    # If no markdown blocks found, try to extract issues from Gemini-style prose
    if not issues:
        # Try to extract bulleted issues with bolded headings
        bullets = re.findall(r'\*\*([A-Za-z\s]+):\*\*\s*([\s\S]+?)(?=\n\*\*|\Z)', output)
        for title, desc in bullets:
            issue = {'issue': title.strip() + ': ' + desc.strip()}
            # Try to guess file from desc if present
            file_match = re.search(r'in ([`\w\./-]+)', desc)
            issue['file'] = file_match.group(1) if file_match else 'N/A'
            issue['severity'] = ''
            issue['confidence'] = ''
            issue['suggestion'] = ''
            issue['line_number'] = 'N/A'
            issue['code'] = 'N/A'
            issues.append(issue)
        # Try to extract recommendations as suggestions
        recs = re.findall(r'\d+\.\s+([\s\S]+?)(?=\n\d+\.|\Z)', output)
        for i, rec in enumerate(recs):
            if i < len(issues):
                issues[i]['suggestion'] = rec.strip()
            else:
                issues.append({'issue': '', 'file': 'N/A', 'severity': '', 'confidence': '', 'suggestion': rec.strip(), 'line_number': 'N/A', 'code': 'N/A'})
    # If still no issues, treat the whole output as a single issue summary
    if not issues:
        issues = [{"issue": output.strip(), 'file': 'N/A', 'severity': '', 'confidence': '', 'suggestion': '', 'line_number': 'N/A', 'code': 'N/A'}]
    issues = filter_false_positives(issues)
    # Remove empty issues (all fields blank except 'file', 'line_number', 'code')
    issues = [i for i in issues if any(v for k, v in i.items() if k not in ('file', 'line_number', 'code'))]
    return issues

def print_issues_markdown(issues, group_by='file'):
    """
    Print issues grouped by file or issue type, with emoji for severity, in CLI-friendly Markdown.
    """
    from collections import defaultdict
    emoji_map = {'critical': '🔒', 'high': '⚠️', 'medium': '⚠️', 'low': '✅'}
    grouped = defaultdict(list)
    for issue in issues:
        key = issue.get(group_by, 'Unknown')
        grouped[key].append(issue)
    for group, group_issues in grouped.items():
        print(f"\n### `{group}`\n")
        for issue in group_issues:
            sev = issue.get('severity', '').lower()
            emoji = emoji_map.get(sev, '❓')
            print(f"{emoji} **Issue:** {issue.get('issue', '')}")
            print(f"   **Severity:** {issue.get('severity', '')}")
            print(f"   **Confidence:** {issue.get('confidence', '')}")
            if issue.get('line_number'):
                print(f"   **Line Number:** {issue.get('line_number')}")
            if issue.get('code'):
                print(f"   **Code:** {issue.get('code')}")
            print(f"   **Suggestion:** {issue.get('suggestion', '')}\n")

def is_placeholder_value(value):
    """
    Returns True if the value is a generic placeholder, not a real secret.
    This is a general check, not a hardcoded list.
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
    # Looks like a template variable
    if re.match(r'<.*>', value):
        return True
    return False

def filter_false_positives(issues):
    """
    Remove issues that are false positives, such as flagged lines with known placeholders
    or complaints about .env not in .gitignore when it is present.
    This logic is general and applies to any prompt or review type.
    """
    # Read .gitignore to check for .env
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
    except Exception:
        gitignore_content = ''
    filtered = []
    for issue in issues:
        # Check all relevant fields for placeholder values
        for field in ['code', 'suggestion', 'issue']:
            val = issue.get(field, '')
            if is_placeholder_value(val):
                break  # skip this issue
        else:
            # .env/.gitignore logic remains
            if (
                issue.get('file', '').strip() == '.gitignore' and
                'not added to' in (issue.get('issue', '').lower() or '') and
                '.env' in gitignore_content
            ):
                continue
            filtered.append(issue)
    return filtered
