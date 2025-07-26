# 📌 AIDiff - LLM-Powered Git Diff Reviewer

## 📄 Overview
AIDiff is a developer tool that scans `git diff` output before a pull request is created. 
It uses LLMs to identify security vulnerabilities (and optionally other issues like accessibility 
or performance problems) in changed code. The initial version is a CLI tool, later intended for 
integration into a VSCode extension.

...

## 🛠 Planned Stack
- Language: Python 3
- CLI Parser: `argparse` or `typer`
- Git Diff: GitPython or raw subprocess call
- API: Support multiple LLMs, OpenAI for MVP
- Config: `.env` file for API keys
- Optional: LangChain later (not required at MVP)

## 🎯 Goals
- Detect and report potential issues in code before PR creation.
- Focus on security, but allow configuration for other review types.
- Make the tool easy to use with minimal manual setup.
- Format output clearly for developers.

---

## 📦 Features

### ✅ Core
- Parse git diff between current branch and base.
- Send diff to an LLM with a prompt tuned for the selected review mode(s).
- Return actionable feedback with:
  - Issue description
  - Severity (low/medium/high/critical)
  - Confidence (0–100%)
  - Suggested fix

### ⚙️ Configurable Modes
- Support multiple review types:
  - `security`
  - `accessibility`
  - `performance`
- Allow mixing modes in one review.

### 🧾 Output
- Markdown-style CLI output
- Clearly formatted with headers and bullet points
- Grouped by file or issue type

---

## 📥 Input
- Git diff output generated automatically (`git diff <base>`)
- Optional mode flags: `--modes security accessibility`
- Optional config for API key (OpenAI, Anthropic, etc.)

---

## 📤 Output Example

```markdown
### 🔒 Security Review

**Issue:** API key detected in `config.js`  
**Severity:** Critical  
**Confidence:** 95%  
**Suggestion:** Move secrets to environment variables.

---

**Issue:** User input is not validated in `formHandler.js`  
**Severity:** High  
**Confidence:** 87%  
**Suggestion:** Use a schema validation library.
