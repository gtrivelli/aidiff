# AIDiff: LLM-Powered Git Diff Reviewer

AIDiff is a CLI tool that uses large language models (LLMs) to review your code changes for security, accessibility, and performance issues before you open a pull request.

## Purpose
- Detect and report potential issues in code before PR creation.
- Focus on security, but allow configuration for other review types.
- Make the tool easy to use with minimal setup.
- Format output clearly for developers.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd aidiff
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set your API keys:**
   - Copy `.env.example` to `.env` and add your OpenAI and/or Gemini API keys.

4. **Run the tool:**
   ```bash
   python main.py --modes security accessibility --provider openai --output markdown
   ```
   - Use `--base <branch>` to specify the base branch (default: origin/main)
   - Use `--include-untracked` to include untracked files
   - Use `--dry-run` to preview the prompt without calling the LLM
   - Use `--debug` to print raw LLM responses

## Example Usage

```bash
# Basic security review
python main.py --modes security --provider openai

# Multi-mode review with Google Gemini
python main.py --modes security accessibility performance --provider google --model gemini-1.5-flash

# Include untracked files and debug output
python main.py --modes security --include-untracked --debug
```

## Programmatic Usage (New)

With the refactored architecture, you can now use AIDiff programmatically:

```python
from aidiff import AIDiffReviewer, ReviewConfig

config = ReviewConfig(
    base_branch="main",
    modes=["security", "performance"],
    provider="openai",
    output_format="markdown"
)

reviewer = AIDiffReviewer(config)
result = reviewer.review()
print(result)
```

## Example Output

```
===== LLM REVIEW RESULTS =====

### `app.py`

🔒 **Issue:** Hardcoded secret key found
   **Severity:** High
   **Confidence:** 95%
   **Suggestion:** Move secret keys to environment variables or a secure vault.

### `templates/index.html`

⚠️ **Issue:** Button missing accessible label
   **Severity:** Medium
   **Confidence:** 90%
   **Suggestion:** Add an aria-label or descriptive text to the button.
```


## CLI Options

| Option                  | Description                                                      |
|------------------------|------------------------------------------------------------------|
| `--base <branch>`      | Base branch to diff against (default: origin/main)                |
| `--staged`             | Only include staged changes in the diff                           |
| `--modes`              | Review modes: security, accessibility, performance                |
| `--include-untracked`  | Include untracked files in the diff                               |
| `--provider`           | LLM provider to use (openai, google, anthropic, etc)              |
| `--model`              | LLM model name (e.g. gpt-4-turbo, gemini-pro, etc)                |
| `--output`             | Output format: markdown or plain                                  |
| `--dry-run`            | Show prompt and diff, but do not call the LLM                     |
| `--debug`              | Print extra debug information (raw LLM response, API call details)|

## Running Tests

To run all unit tests:

```bash
# Run all tests (requires virtual environment)
source .venv/bin/activate
PYTHONPATH=/path/to/aidiff python -m unittest tests.test_core tests.test_refactored -v

# Or run specific test suites
python -m unittest tests.test_refactored.TestPromptManager -v
```

## Extending AIDiff

### Adding a New LLM Provider

```python
from aidiff.providers import LLMProvider

class MyCustomProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_response(self, prompt: str, model: str = None) -> str:
        # Your implementation here
        return "Generated response"
    
    def get_default_models(self) -> tuple:
        return ("my-model-v1", "my-model-v2")

# Register the provider
from aidiff.providers.factory import LLMProviderFactory
LLMProviderFactory._providers["mycustom"] = MyCustomProvider
```

### Adding a New Output Format

```python
from aidiff.formatters import OutputFormatter

class MyCustomFormatter(OutputFormatter):
    def format_issues(self, issues, group_by='file'):
        # Your custom formatting logic
        return "Formatted output"

# Register the formatter  
from aidiff.formatters.factory import FormatterFactory
FormatterFactory._formatters["custom"] = MyCustomFormatter
```

---

For more details, see the [copilot_checklist.md](copilot_checklist.md).
