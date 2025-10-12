# Job Application Automation - Todo List

## In Progress

### Helper Scripts Audit
- [~] Audit remaining helper scripts for reuse vs. diagnostics !!!
    - [x] Identify overlap with utils modules (see info/HELPERS.md)
    - [x] Refactor low-risk helpers to call utils (inspect_html uses utils.html; trello helpers use utils.trello)
    - [x] Add short README notes for purely diagnostic scripts (info/HELPERS.md)
    - [ ] Optional: unify helpers under a single diagnostics CLI entrypoint

### Environment Variable Cleanup
- [x] Create central config module
- [x] Update cover_letter_ai.py (now cover_letter.py)
- [x] Update trello_manager.py (replaced by trello_connect.py)
- [x] Update remaining modules (app.py, main.py)
- [x] Add environment validation to startup

### Code Organization
- [x] Create config module for environment variables
- [~] Add type hints (in progress)
    - [x] utils/env.py (core module)
    - [~] scraper.py (partial)
    - [x] trello_connect.py (was trello_manager.py)
    - [x] cover_letter.py (was cover_letter_ai.py)
    - [x] docx_generator.py
    - [x] pdf_generator.py
    - [x] main.py
    - [x] app.py
- [x] Review and complete type hints in all modules
- [x] Move helper functions to appropriate modules
    - [x] Create utils.html with helpers (src/utils/html.py)
    - [x] Refactor inspect_html to use utils.html
    - [x] Create utils.trello for auth helpers (src/utils/trello.py)
    - [x] Refactor trello_inspector to use utils.trello
    - [x] Refactor test_trello_auth to use env-based auth
- [ ] Document public APIs

## Not Started

### Improve Test Coverage
- [x] Add tests for config.py module
- [x] Add tests for scraper.py (0% → 80%)
- [x] Add tests for trello_connect.py (basic request payload tests)
- [x] Add tests for main.py (integration via process_job_posting)
- [x] Add tests for app.py (route tests for /, /process, /status, /download)
- [x] Improve cover_letter_ai.py coverage (47% → 80%)
    - Added init/env, detection, exception, save, and prompt variant tests
- [x] Improve cover_letter.py coverage (47% → 80%)
    - Added prompt content assertions and default save path test
- [x] Improve docx_generator.py coverage (26% → 80%)
    - Added split-placeholder replacement, table cell replacement, and save error tests
- [x] Add unit tests for utils.html (JSON-LD extraction, keyword search)
- [x] Add unit tests for utils.trello (mask_secret, get_auth_params)
- [x] Add unit tests for scraper utilities (clean_job_title, split_address)
- [x] Integration test for process_job_posting (mock network/Trello; use saved HTML fixture)
- [x] Flask route tests: /process, /status/<job_id>, /download/<path>
- [x] DOCX/PDF fallback tests (docx2pdf fallback path, pdf_generator minimal generation)
- [x] Cover letter length checks (prompt word-count enforcement)
- [x] Scraper JSON-LD happy-path parsing test
- [x] CoverLetterGenerator happy-path test (200-word output)

### Error Handling & Logging
- [~] Add proper error handling for API calls
    - [x] TrelloConnect: return None and log on non-retryable errors; include short stdout note for tests
    - [~] Extend to scraper, cover letter, and document generators
        - Scraper (src/scraper.py)
            - [x] Wrap network calls with utils/http.request_with_retries; handle timeouts/connection errors
            - [x] On non-200 responses (403/404/5xx), raise ScraperError with URL and status; log details
            - [x] Avoid prints; return None or a minimal safe payload upstream; document behavior
            - [x] Tests: network error, 404, malformed HTML path
        - Cover letter (src/cover_letter.py)
            - [x] Catch OpenAI API exceptions (timeouts/quota); raise AIGenerationError; log context (no secrets)
            - [x] Enforce 180–240 words; if violation, log warning and raise AIGenerationError
            - [x] Tests: API exception path; word-count enforcement failure
        - Document generators (src/docx_generator.py, src/pdf_generator.py)
            - [x] Guard missing templates and bad placeholders; raise DocumentError; log actionable message
            - [x] PDF: handle missing docx2pdf on non-Windows; ensure graceful fallback messaging
            - [x] Tests: template missing, docx2pdf absent, conversion error fallback
- [x] Implement retry mechanisms
    - [x] Trello card creation: small retry with backoff on 429/5xx
    - [x] Consider centralizing retries via utils/http.py and adjust tests accordingly
        - [x] Scope decision: Scraper already uses utils/http.request_with_retries; apply to TrelloConnect only
        - [x] Refactor TrelloConnect to call utils/http.request_with_retries (inject requester/session for tests)
        - [x] Update unit tests to patch the injected requester instead of requests.post; keep stdout hook
        - [x] Add targeted tests for utils/http backoff on 429/5xx and non-retryable handling
- [x] Replace print statements with logging
    - [x] Introduced utils/logging.get_logger and applied across core modules
    - [x] Removed remaining prints in core modules; kept a single Trello stdout line as an intentional test hook
- [x] Add error reporting
    - [x] Create centralized reporter (src/utils/error_reporting.py) with JSON event files under output/errors
    - [x] Wire into main workflow on critical failures (scrape empty, cover letter failure)
    - [x] Add Flask global error handler to record unhandled exceptions
    - [x] Add unit tests for reporter (sanitization, file writing, severity logging)
    - [x] Add integration test asserting error file created on simulated failures
    - [x] Optional: expose last N errors via /history or dedicated /errors endpoint (without sensitive data)

### Documentation Updates
- [ ] Update README.md with latest changes
- [ ] Add API documentation
- [ ] Add contribution guidelines
- [ ] Add development setup guide
- [ ] Document helper scripts and their diagnostic purpose

## Completed

- [x] Run tests and fix fallout (all tests passing)
- [x] TrelloConnect: kept direct requests.post for test monkeypatch compatibility and added a retry loop
- [x] Migrated core modules from print to logging; retained Trello stdout hook for unit test; full suite green (41/41)