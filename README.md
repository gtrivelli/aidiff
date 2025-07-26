# AIDiff: LLM-Powered Git Diff Reviewer

AIDiff is a CLI tool that uses large language models (LLMs) to review your code changes for security, accessibility, and performance issues before you open a pull request.

## Purpose
- Detect and report potential issues in code before PR creation.
- Focus on security, but allow configuration for other review types.
- Make the tool easy to use with minimal manual setup.
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
python main.py --modes security --include-untracked --provider google --model models/gemini-1.5-flash --output markdown
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

To run all unit tests and sample diff tests:

```bash
python3 -m unittest discover tests
```

---

For more details, see the [copilot_checklist.md](copilot_checklist.md).
