# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2025-10-13

Milestone: Enhanced cover letter generation with context-aware salutations and comprehensive Trello integration.

### Added
- Context-aware cover letter salutations and valedictions:
  - Automatic German formality detection (du vs. Sie) via pronoun counting
  - Personalized greetings using contact names when available
  - Generic team greetings as fallback
  - Tone matching to seniority level (junior/mid/senior/executive)
  - AI prompt includes formality instructions for German cover letters
  - Three-part structure: salutation, body, valediction stored in job_data
  - DOCX template placeholders: {{COVER_LETTER_SALUTATION}}, {{COVER_LETTER_VALEDICTION}}
  - 25 new unit tests for formality detection, salutation/valediction generation (128 total tests)
- Comprehensive Trello card layout improvements:
  - Structured markdown descriptions with key facts, source IDs, and company info
  - Automatic enrichment: language detection, seniority detection, work mode normalization
  - Label mapping for work mode, language, and seniority
  - Custom field population (company name, job title, source, publication date)
  - Idempotency checks to prevent duplicate cards
  - Full documentation in docs/TRELLO_CARD_LAYOUT.md

### Fixed
- GitHub Actions CI: Added required environment variables for test execution

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