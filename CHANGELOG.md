# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-10-12

Milestone: Core workflow stabilized, diagnostics added, and documentation completed.

### Added
- Centralized error reporting (sanitized JSON events under `output/errors`) and `/errors` endpoint in Flask.
- Diagnostics CLI (`python -m src.helper.cli` or `jobapp-diag`) with subcommands:
  - `inspect-html` (headers, data-at elements, JSON-LD, keyword search)
  - `trello-auth` (verify credentials, mask secrets)
  - `trello-inspect` (board info, lists, labels)
- DOCX/PDF generation robustness with fallbacks.
- VS Code test task that works with Windows path quoting.

### Changed
- Trello integration refactored into `src/trello_connect.py` using centralized HTTP retries.
- Cover letter generator unified in `src/cover_letter.py` with strict 180–240 word enforcement and language/seniority detection.
- Global Flask error handling improved: 404s no longer create error events; `/favicon.ico` served as 204.
- Scraper hardened: JSON-LD first, DOM fallback; better error handling.

### Fixed
- PDF style name bug in `pdf_generator.py`.
- Retry helper incorrectly retrying on non-retryable HTTPError (now short-circuits).
- PowerShell path quoting breaking VS Code tasks.
- /errors listing sorted by event timestamp (timezone-aware UTC).

### Docs
- Updated `README.md` with endpoints, diagnostics CLI, error reporting, and Windows setup.
- Added `docs/API.md`, `CONTRIBUTING.md`, `docs/DEVELOPMENT.md`.
- Added `info/HELPERS.md` describing helper scripts and diagnostics.

[0.1.0]: https://github.com/YOUR_USERNAME/job-application-automation/releases/tag/v0.1.0