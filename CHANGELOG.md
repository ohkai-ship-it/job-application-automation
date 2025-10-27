# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.1] - 2025-10-27

### Fixed
- **Python 3.10 Compatibility**: 
  - Replaced `datetime.UTC` (Python 3.11+) with `timezone.utc` for universal compatibility
  - Fixed in `src/utils/error_reporting.py`
- **Python 3.12 Deprecation Warnings**:
  - Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
  - Fixed in `src/app.py` (health check endpoints) and `src/logging_config.py`
- **CI Test Suite**:
  - Fixed `test_cover_letter_happy_path` with comprehensive file I/O mocking
  - Fixed `test_load_env` with correct module namespace mocking
  - Fixed `test_create_card_with_labels_and_custom_fields` by using correct Trello env var names
  - All 109 tests now passing on Python 3.10 CI runner
- **CI/CD Workflow**:
  - Made Codecov upload non-blocking to prevent CI failures due to external rate limits
  - Set `fail_ci_if_error: false` and added `continue-on-error: true`

### Changed
- **Code Quality**: 
  - Removed 7 incomplete test files (.skip variants) - ~655 lines
  - Removed 2 unused utility modules (figma_client.py, page_analyzer.py) - ~700 lines
  - Consolidated CLI from src/helper → src/utils
- **Documentation**:
  - Enhanced BACKLOG.md with comprehensive roadmap and effort estimates
  - Improved CONTRIBUTING.md with detailed development guidelines (200 lines)
  - Simplified CHANGELOG.md for clarity and v0.2.0 focus

## [0.3.0] - 2025-10-16

Milestone: Database integration for duplicate detection and AI cost tracking.

### Added
- **SQLite Database Layer** (`src/database.py`):
  - Lightweight 2-table schema for duplicate detection and AI metadata tracking
  - `processed_jobs` table: SHA256-based URL deduplication with Trello card links
  - `generation_metadata` table: AI model, cost, word count, and generated text tracking
  - Singleton pattern with context managers for safe connections
  - 6 indexed queries for performance (duplicate check, recent jobs, search, stats, cost tracking)
  - Comprehensive unit tests (6/6 passing)
  - Philosophy: Support tool for duplicates, NOT application management (Trello remains source of truth)
- **Database Integration**:
  - Step 0 in `main.py`: Duplicate detection before scraping (warns but continues in testing mode)
  - Database saving after successful processing (job data + AI metadata + Trello links)
  - Non-blocking integration: database failures don't stop workflow
  - Flask app ready for background job integration (`from database import get_db`)
- **Initialization & Testing**:
  - `src/helper/init_database.py`: One-command database setup
  - `src/helper/test_database_integration.py`: End-to-end integration tests
  - Production database created at `data/applications.db`
- **Documentation**:
  - `docs/DATABASE_SCHEMA.md`: Complete schema design with examples and queries
  - `docs/INTEGRATION_STRATEGY.md`: Comprehensive integration roadmap (10 integration options)
  - `docs/PRODUCT_ROADMAP.md`: Phased implementation plan (Q1-Q4 2025), portfolio showcase strategy
  - `docs/FIGMA_AI_PROMPT.md`: Dashboard design specifications for future UI implementation

### Changed
- **Cover Letter Validation** (Testing Mode):
  - Relaxed word count validation from 180-240 to 170-250 words (testing only)
  - AI prompt still requests strict 180-240 range
  - Logs info message when word count is acceptable but not ideal
  - TODO added for production tightening
- **Dependency Updates**:
  - Added `pypdf` to requirements.txt (CV PDF reading)
  - Installed `pypdf` in virtual environment

### Fixed
- CV file loading: `pypdf` package was missing from environment
- Database save on duplicates: Now checks duplicate status before saving to avoid UNIQUE constraint errors
- Cover letter generation: Path resolution for CV files works correctly

### Developer Notes
- **Testing Mode Active** (⚠️ **Before Production**):
  - Duplicate detection warns but continues (uncomment `return` in `main.py` Step 0 to stop on duplicates)
  - Cover letter validation accepts 170-250 words (change back to 180-240 in `cover_letter.py`)
- **Database Philosophy**: Tracks what was processed, NOT application status (Trello owns that)
- **Next Steps**: Multi-AI providers, improved UI, LinkedIn integration

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