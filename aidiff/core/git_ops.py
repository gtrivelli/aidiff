"""Git operations module."""

import subprocess
from typing import List, Optional
from aidiff.core.exceptions import GitError


class GitOperations:
    """Handles Git operations for diff extraction."""

    @staticmethod
    def is_dirty_working_tree() -> bool:
        """Check if the working tree has uncommitted changes."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to check git status: {e}")

    @staticmethod
    def get_git_diff(base_branch: str, staged: bool = False) -> str:
        """Get git diff output."""
        try:
            if staged:
                diff_cmd = ['git', 'diff', '--cached', base_branch]
            else:
                diff_cmd = ['git', 'diff', base_branch]
            
            result = subprocess.run(
                diff_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise GitError(f"Error running git diff: {e}")

    @staticmethod
    def get_untracked_files() -> List[str]:
        """Get list of untracked files."""
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--exclude-standard'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return [f for f in result.stdout.splitlines() if f]
        except subprocess.CalledProcessError as e:
            raise GitError(f"Error getting untracked files: {e}")

    @staticmethod
    def get_untracked_file_diff(file_path: str) -> str:
        """Generate diff for an untracked file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            diff = f"diff --git a/{file_path} b/{file_path}\nnew file mode 100644\n--- /dev/null\n+++ b/{file_path}\n"
            for line in content.splitlines():
                diff += f"+{line}\n"
            return diff
        except Exception as e:
            return f"# Could not read untracked file {file_path}: {e}\n"
