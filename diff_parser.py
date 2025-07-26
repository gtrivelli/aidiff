# Git diff parsing logic will go here

def preserve_full_diff_format(diff_text):
    """
    Preserve the full Git diff output format, including file boundary markers like:
    'diff --git a/file1.js b/file1.js'.
    This function returns the diff unchanged to ensure all structure is kept.
    """
    return diff_text

def clean_diff(diff_text):
    """
    Strip irrelevant metadata from a git diff, but keep file boundaries, hunk headers, and diff lines.
    """
    cleaned = []
    for line in diff_text.splitlines():
        if line.startswith('diff --git a/'):
            cleaned.append(line)
        elif line.startswith('@@'):
            cleaned.append(line)
        elif line.startswith('+') or line.startswith('-') or line.startswith(' '):
            cleaned.append(line)
        # Ignore lines like 'index ...', 'new file mode ...', etc.
    return '\n'.join(cleaned)
