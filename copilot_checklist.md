# 🧩 AIDiff Development Checklist (Step-by-Step)

## ✅ Step 1: Project Setup
- [x] Initialize Python project
- [x] Create virtual environment
- [x] Add `requirements.txt` with needed dependencies (`openai`, `python-dotenv`, `GitPython`, etc.)
- [x] Set up basic folder structure:
    aidff/
├── main.py
├── reviewer.py
├── diff_parser.py
├── prompts/
│ └── security.md
│ └── accessibility.md
│ └── performance.md
├── utils.py
├── config.py
├── README.md
├── .env.example
└── tests/

---

## ✅ Step 2: Git Diff Handling
### 2.a - Get diff between HEAD and base branch
- [x] Accept base branch as CLI argument
- [x] Use `git diff` to get patch (raw format)
- [x] Handle dirty working tree (optional)

### 2.b - Format diff for prompt input
- [x] Implement logic to run git diff and capture staged or working changes.
- [x] Preserve full Git diff output format, including file boundary markers like: `diff --git a/file1.js b/file1.js`
- [x] Strip any irrelevant metadata or excessive context if necessary, but keep the diff readable and structured.
- [x] Optionally include untracked files in the diff output (with --include-untracked flag)

---

## ✅ Step 3: Prompt & Mode Engine
### 3.a - Load prompt templates
- [x] Read Markdown/Plaintext files from `prompts/`
- [x] Combine multiple prompt files if multiple modes selected

### 3.b - Inject diff into final prompt
- [x] Use clean formatting
- [x] Optional: truncate overly large diffs (warn if so)

---

## ✅ Step 4: LLM Integration
### 4.a - API Key Handling
- [x] Load from `.env` or `OPENAI_API_KEY` env var
- [x] Fail gracefully with helpful error if missing

### 4.b - Send prompt to LLM
- [x] Use `openai.ChatCompletion.create()`
- [x] Use GPT-4 by default, fallback to GPT-3.5 if needed
- [x] Parse and validate response

---

## ✅ Step 5: Output Formatting
### 5.a - Parse LLM output structure
- [x] Identify each issue block (file, severity, confidence, suggestion)

### 5.b - Print in CLI-friendly Markdown
- [x] Group by file or issue type
- [x] Add emoji for visual clarity (e.g. ✅, 🔒, ⚠️)

---

## ✅ Step 6: CLI Interface
- [x] Use `argparse` or `typer` to accept:
  - `--base <branch>` (default: origin/main)
  - `--modes security accessibility`
  - `--output markdown/plain`
- [x] Optional: `--dry-run` or `--debug`

---

## ✅ Step 7: Testing & Sample Inputs
- [x] Add sample `diff.txt` files for testing
- [x] Write unit tests for:
  - Prompt assembly
  - Diff parsing
  - LLM output handling

---

## ✅ Step 8: Polish
- [x] Update README as needed with:
  - Purpose
  - Setup instructions
  - Example usage
  - Sample output
- [x] Create `.env.example` with placeholder API key
- [x] Add MIT license

---

## 🧩 Future (Post-MVP)
- [ ] Package as pip-installable CLI
- [ ] Add VSCode extension wrapper
- [ ] Add GitHub Action support
- [ ] Explore integrating OSS LLMs via Hugging Face
