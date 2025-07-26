# Utility functions for AIDiff

import re

# Only keep the regex that is actually used
MARKDOWN_BULLET_REGEX = r'\*\*([A-Za-z\s]+):\*\*\s*([\s\S]+?)(?=\n\*\*|\Z)'

def parse_llm_output(output):
    """
    Parse the LLM output and identify each issue block (file, severity, confidence, suggestion).
    Returns a list of dicts, one per issue.
    Handles both markdown and prose output from LLMs like Gemini.
    Enhanced to handle Gemini's prose/numbered-list style.
    Now robustly handles multi-line and code block fields (especially **Code:**).
    Streamlined for readability and maintainability.
    Consolidates markdown and prose parsing into a single approach.
    Uses simple line splitting and prefix checks for markdown fields for clarity.
    Handles code blocks robustly, supporting variations in delimiters (e.g., ```, ``).
    """
    issues = []
    issue_blocks = re.split(r'---+', output)
    for block in issue_blocks:
        block = block.strip()
        if not block:
            continue
        issue = {}
        lines = block.splitlines()
        field = None
        value_lines = []
        in_code_block = False
        code_block_delim = None
        # Map markdown field names to dict keys
        field_map = {
            'File': 'file',
            'Issue': 'issue',
            'Severity': 'severity',
            'Confidence': 'confidence',
            'Suggestion': 'suggestion',
            'Line Number': 'line_number',
            'Code': 'code',
        }
        for line in lines:
            line_stripped = line.strip()
            # Check for markdown field prefix directly, no need for regex or looping
            matched_field = None
            for markdown_field, dict_key in field_map.items():
                prefix = f"**{markdown_field}:**"
                if line_stripped.startswith(prefix) and not in_code_block:
                    matched_field = markdown_field
                    break
            if matched_field:
                # Save previous field
                if field and value_lines:
                    val = '\n'.join(value_lines).strip()
                    if field == 'Code' and code_block_delim:
                        val = re.sub(rf'^{re.escape(code_block_delim)}[a-zA-Z0-9]*', '', val)
                        val = re.sub(rf'{re.escape(code_block_delim)}$', '', val).strip()
                    issue[field_map.get(field, field.lower().replace(' ', '_'))] = val
                field = matched_field
                val = line_stripped[len(f"**{matched_field}:**"):].lstrip()
                # Detect code block delimiter (``` or ``)
                if field == 'Code' and (val.startswith('```') or val.startswith('``')):
                    in_code_block = True
                    code_block_delim = val[:3] if val.startswith('```') else val[:2]
                    value_lines = [val]
                else:
                    in_code_block = False
                    code_block_delim = None
                    value_lines = [val] if val else []
            else:
                if field == 'Code' and (in_code_block or (line_stripped.startswith('```') or line_stripped.startswith('``'))):
                    value_lines.append(line)
                    # End code block if delimiter found
                    if code_block_delim and line_stripped.startswith(code_block_delim):
                        in_code_block = False
                elif field:
                    value_lines.append(line)
        # Save last field
        if field and value_lines:
            val = '\n'.join(value_lines).strip()
            if field == 'Code' and code_block_delim:
                val = re.sub(rf'^{re.escape(code_block_delim)}[a-zA-Z0-9]*', '', val)
                val = re.sub(rf'{re.escape(code_block_delim)}$', '', val).strip()
            issue[field_map.get(field, field.lower().replace(' ', '_'))] = val
        issues.append(issue)
    # If still no issues, treat the whole output as a single issue summary
    if not issues:
        issues = [{"issue": output.strip(), 'file': 'N/A', 'severity': '', 'confidence': '', 'suggestion': '', 'line_number': 'N/A', 'code': 'N/A'}]
    issues = filter_false_positives(issues)
    # Remove empty issues: must have at least one of issue, suggestion, severity, or confidence non-empty
    def is_real_issue(i):
        important_fields = ['issue', 'suggestion', 'severity', 'confidence']
        if not any(i.get(f, '').strip() for f in important_fields):
            return False
        code_val = i.get('code', '')
        if not code_val.strip():
            i['code'] = ''
        return True
    issues = [i for i in issues if is_real_issue(i)]
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
    Also skips issues where the 'issue' field is just a generic field label (e.g., 'suggestion', 'issue', etc.)
    """
    # Read .gitignore to check for .env
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
    except Exception:
        gitignore_content = ''
    filtered = []
    generic_fields = {'suggestion', 'issue', 'severity', 'confidence', 'file', 'code', 'line number'}
    for issue in issues:
        # Check all relevant fields for placeholder values
        for field in ['code', 'suggestion', 'issue']:
            val = issue.get(field, '')
            if is_placeholder_value(val):
                break  # skip this issue
        else:
            # Skip if 'issue' field is just a generic field label or empty
            issue_val = (issue.get('issue') or '').strip().lower()
            if issue_val in generic_fields or not issue_val or re.fullmatch(r'^[\W_]+$', issue_val):
                continue
            # .env/.gitignore logic remains
            if (
                issue.get('file', '').strip() == '.gitignore' and
                'not added to' in (issue.get('issue', '').lower() or '') and
                '.env' in gitignore_content
            ):
                continue
            filtered.append(issue)
    return filtered
