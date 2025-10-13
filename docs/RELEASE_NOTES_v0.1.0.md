# Release Notes: v0.1.0 (2025-10-12)

This release marks a solid milestone with a stabilized core pipeline, better observability, and comprehensive documentation.

Highlights
- Centralized error reporting with `/errors` endpoint and sanitized JSON event files.
- Diagnostics CLI (`python -m src.helper.cli` / `jobapp-diag`) for HTML/Trello inspection.
- Strict cover-letter length control (180–240 words), language/seniority detection, and DOCX/PDF fallbacks.
- Improved scraper (JSON-LD first, DOM fallback) and Trello integration with retries.

Install / Upgrade
- Ensure dependencies from `requirements.txt` are installed.
- Set credentials in `config/.env` (OPENAI_API_KEY, TRELLO_*).

Usage
- Web UI: `python src/app.py` then open http://127.0.0.1:5000
- CLI orchestrator: `python src/main.py <url>`
- Diagnostics: `python -m src.helper.cli ...` or `jobapp-diag ...`

Notable Fixes
- Corrected PDF style creation; stopped retries on non-retryable HTTP errors.
- Stable Windows test task with proper path quoting.
- Error list sorted by event timestamp; 404s no longer recorded as errors; `/favicon.ico` route returns 204.

Thanks for contributing and testing! If you hit issues, check `output/errors` and open an issue with the sanitized event details.
