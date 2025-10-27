# Contributing

Thanks for your interest in improving Job Application Automation! This guide will help you get started.

---

## Getting Started

### 1. Fork & Clone
```powershell
git clone https://github.com/YOUR_USERNAME/job-application-automation.git
cd job-application-automation
git remote add upstream https://github.com/ohkai-ship-it/job-application-automation.git
```

### 2. Create a Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest pytest-cov  # for testing
```

### 3. Configure Environment
```powershell
cp config/.env.example config/.env
# Edit config/.env with your Trello and OpenAI credentials
```

---

## Branching Model

- **`master`** – Production releases (stable, tagged)
- **`develop`** – Integration branch (primary development)
- **`feature/<name>`** – New features (branch from `develop`)
- **`fix/<name>`** – Bug fixes (branch from `develop`)

**All PRs go to `develop`**, except hotfixes which can target `master`.

---

## Development Workflow

### Before You Start
1. Check [BACKLOG.md](BACKLOG.md) for planned features
2. Search existing issues to avoid duplicates
3. Discuss larger changes in an issue first

### Making Changes

```powershell
# Create feature branch
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name

# Make changes and test
# ... edit files ...
pytest -q

# Commit with clear messages
git add .
git commit -m "Add feature: clear description of change"
git push origin feature/your-feature-name
```

### Submit a PR
1. Push your branch to your fork
2. Open a Pull Request against `develop`
3. Link any related issues
4. Include a brief summary of changes and testing notes
5. Request review from maintainers

---

## Testing

### Running Tests

```powershell
# Using VS Code task (recommended)
# Press Ctrl+Shift+B or Run Task → "Run tests"

# Or directly via CLI
pytest -q

# With coverage report
pytest --cov=src tests/
```

### Writing Tests

- Use `pytest` framework (see `tests/` for examples)
- Write deterministic tests (no random data or timing dependencies)
- Test both happy path and error cases
- Mock external APIs (Trello, OpenAI) in tests

### Test Coverage Goals
- **Target**: >80% coverage on `src/`
- **Priority**: Core logic (scraper, cover letter generation, Trello integration)
- **Nice to have**: Edge cases, error paths

---

## Code Style & Standards

### Python Style
- **Version**: Python 3.8+
- **Type hints**: Use where practical (`def process(url: str) -> dict:`)
- **Naming**: descriptive names (avoid `a`, `x`, `tmp`)
- **Functions**: Prefer small, focused functions (single responsibility)

### Imports & Organization
```python
# Standard library
import json
import os

# Third-party
import requests

# Local
from src.utils.logging import get_logger
from src.utils.errors import JobScraperError
```

### Logging
```python
# ✅ Good
logger = get_logger(__name__)
logger.info(f"Processing {url}")

# ❌ Bad
print(f"Processing {url}")  # Use logging instead
```

### Error Handling
```python
# ✅ Good
from src.utils.errors import JobScraperError

def scrape_job(url: str) -> dict:
    try:
        # ...
    except Exception as e:
        raise JobScraperError(f"Failed to scrape {url}") from e

# ❌ Bad
def scrape_job(url: str) -> dict:
    return some_result()  # No error handling
```

---

## Secrets & Credentials

### DO NOT commit:
- API keys, tokens, or passwords
- Configuration with real credentials
- Personal CVs or cover letters
- Test databases with real data

### DO use:
- `config/.env` for local credentials (git-ignored)
- `config/.env.example` as a template
- Environment variable names in docs

### Masking Secrets in Logs
```python
# From src/utils/trello.py
def mask_secret(secret: str, visible_chars: int = 4) -> str:
    """Mask API key, showing only first N chars"""
    return f"{secret[:visible_chars]}{'*' * (len(secret) - visible_chars)}"

logger.info(f"Key: {mask_secret(key)}")  # Shows: Key: abcd****
```

---

## Commits & Pull Requests

### Commit Messages
- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Add details in the body if needed

```
Add language detection to cover letter generator

- Analyzes job description for DE/EN keywords
- Falls back to English if unclear
- Includes unit tests for both languages
```

### PR Description
```markdown
## What
Brief description of changes

## Why
Motivation and context

## How
Technical approach taken

## Testing
How to test locally

## Screenshots/Output
Before/after if applicable
```

---

## Documentation

If your change affects user-facing behavior:
1. Update relevant doc in `docs/`
2. Update `README.md` if it's a major feature
3. Update `BACKLOG.md` if you're implementing a planned feature

---

## Common Tasks

### Adding a New Scraper
1. Create `src/new_scraper.py` following existing patterns
2. Output normalized `job_data` dict (see `src/scraper.py` for schema)
3. Add unit tests in `tests/test_new_scraper.py`
4. Update `docs/SCRAPER_ARCHITECTURE.md` with notes

### Modifying Trello Integration
1. Changes go in `src/trello_connect.py`
2. Test with real Trello board credentials
3. Document field mappings in `docs/TRELLO_CARD_LAYOUT.md`

### Adding CLI Command
1. Add subcommand to `src/utils/cli.py`
2. Follow existing command patterns (arg parsing, error handling)
3. Test via `python -m src.utils.cli <command> --help`

---

## Reporting Issues

When reporting bugs:
1. **Title**: Clear one-liner (not "It doesn't work")
2. **Description**: Steps to reproduce
3. **Expected vs Actual**: What you expected vs what happened
4. **Environment**: Python version, OS, relevant configs
5. **Logs**: Paste relevant errors (sanitize secrets!)

---

## Asking Questions

- **Questions?** Open a discussion issue
- **Need help?** Check docs first, then ask
- **Found docs unclear?** That's a docs PR opportunity!

---

## Code Review

### Checklist for Reviewers
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] No new warnings/lint errors
- [ ] Secrets not committed
- [ ] Documentation updated if needed

### Checklist for Authors
- [ ] Tests pass locally
- [ ] No print statements (use logging)
- [ ] Secrets not included
- [ ] Commits are clear and focused

---

## Recognition

Contributors are recognized in:
- PR comments (thanks!)
- Potential future CONTRIBUTORS file

Thank you for contributing! 🎉
