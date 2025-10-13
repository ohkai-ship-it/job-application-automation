# Development Setup Guide

This guide helps you get a dev environment running on Windows PowerShell.

## Prerequisites
- Python 3.8+
- VS Code (recommended)

## Environment
```powershell
# Create a venv (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Environment variables
- Create `config/.env` and set values:
  - OPENAI_API_KEY
  - TRELLO_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID, TRELLO_LIST_ID_LEADS
- Some modules still read root `.env`; prefer `config/.env` and exporting to your shell.

## Running
- Flask UI:
```powershell
python src/app.py
```

- CLI orchestrator:
```powershell
python src/main.py https://www.stepstone.de/...
```

- Diagnostics CLI:
```powershell
python -m src.helper.cli inspect-html --file data/debug_page.html
python -m src.helper.cli trello-auth
python -m src.helper.cli trello-inspect
```

## Tests
- VS Code: Run Task → "Run tests"
- CLI:
```powershell
pytest -q
```

## Troubleshooting
- docx2pdf not available: PDF conversion may return None; DOCX will still be generated.
- Trello auth errors: verify TRELLO_* variables in `config/.env`.
- OpenAI errors: ensure OPENAI_API_KEY is set; watch for word-count enforcement (180–240 words).
- Error files: check `output/errors` for latest events.
