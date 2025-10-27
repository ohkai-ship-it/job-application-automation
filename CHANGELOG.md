# Changelog

All notable changes to this project will be documented in this file. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

Planned features and improvements. See [BACKLOG.md](BACKLOG.md) for details.

- [ ] XING and Indeed job board integration
- [ ] Batch scrape CLI subcommand
- [ ] Browser extension for URL capture
- [ ] Advanced job analytics and reporting
- [ ] Parallel processing for multiple URLs

## [0.2.0] - 2025-10-27

**Milestone: Production-ready self-hosted tool with cleanup and optimization**

### Added
- **CLI Consolidation**: Moved diagnostics CLI from `src/helper/cli.py` to `src/utils/cli.py` for cleaner package structure
- **Portfolio Integration**: Added `{{SENDER_PORTFOLIO}}` placeholder for cover letter templates (default: ohkai-ship-it.github.io)
- **Repository Cleanup**: Removed 170+ development/debug files to streamline public repository
- **Enhanced Documentation**: Improved README.md, added comprehensive BACKLOG.md and updated CONTRIBUTING.md

### Changed
- **Module Reorganization**: All utilities now consolidated under `src/utils/` (removed empty `src/helper/` directory)
- **Setup Entry Point**: Updated `setup.py` to reference `src.utils.cli:main` for diagnostics command

### Fixed
- README formatting issues (removed duplicate content)
- Repository size reduced by ~1,337 lines of development artifacts
- Clearer documentation structure for new users

---

## [0.1.0] - 2025-10-12

**Milestone: Core workflow stabilized with Trello integration and AI cover letters**

### Added
- **Job Scraping**:
  - Stepstone scraper with JSON-LD extraction and DOM fallback
  - LinkedIn Collections scraper with Playwright for JS rendering
  - Normalized `job_data` schema for consistent processing
  
- **Trello Integration**:
  - Automatic card creation with intelligent fields
  - Language, seniority, and work mode detection
  - Custom field mapping and label management
  - Duplicate prevention checks
  
- **AI Cover Letter Generation**:
  - Context-aware bilingual generation (German/English)
  - Formality detection and tone matching
  - Strict 180–240 word count enforcement
  - Context-aware salutations and valedictions (du/Sie detection)
  
- **Export Formats**:
  - DOCX generation with professional templates
  - PDF export with styling
  - TXT plain text fallback
  
- **Web UI (Flask)**:
  - Background job processing with `/process` endpoint
  - Status tracking and download capabilities
  - Global error handling and reporting
  
- **Diagnostics CLI**:
  - `trello-auth` – Verify Trello credentials
  - `trello-inspect` – View board configuration
  - `inspect-html` – Debug HTML structure and JSON-LD
  
- **Comprehensive Documentation**:
  - SETUP_GUIDE.md for new users
  - CONTRIBUTING.md for developers
  - docs/DEVELOPMENT.md, docs/TRELLO_CARD_LAYOUT.md, docs/API.md
  - Error reporting with sanitized JSON events

### Changed
- Trello integration refactored into modular `src/trello_connect.py`
- Cover letter generation unified with language/seniority detection
- Global Flask error handling improved
- Scraper hardened with better error recovery

### Fixed
- PDF style name bug in `pdf_generator.py`
- Retry helper incorrectly retrying on non-retryable HTTPError
- PowerShell path quoting in VS Code tasks
- Error event sorting (timezone-aware UTC)

---

## Release Notes

**Current Version**: v0.2.0 (Production)  
**Status**: Ready for self-hosted deployment  
**Platforms**: Windows, macOS, Linux  
**Python**: 3.8+  

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

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