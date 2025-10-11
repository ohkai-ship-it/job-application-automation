# Job Application Automation - Todo List

## In Progress


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
- [ ] Add tests for config.py module
- [ ] Add tests for scraper.py (0% → 80%)
- [x] Add tests for trello_connect.py (basic request payload tests)
- [ ] Add tests for main.py (0% → 70%)
- [ ] Add tests for app.py (0% → 70%)
- [ ] Improve cover_letter_ai.py coverage (47% → 80%)
- [ ] Improve docx_generator.py coverage (26% → 80%)
 - [x] Add unit tests for utils.html (JSON-LD extraction, keyword search)
 - [x] Add unit tests for utils.trello (mask_secret, get_auth_params)
 - [x] Add unit tests for scraper utilities (clean_job_title, split_address)
 - [x] Integration test for process_job_posting (mock network/Trello; use saved HTML fixture)
 - [x] Flask route tests: /process, /status/<job_id>, /download/<path>
 - [ ] DOCX/PDF fallback tests (docx2pdf fallback path, pdf_generator minimal generation)
 - [ ] Cover letter length checks (prompt word-count enforcement)

### Error Handling & Logging
- [ ] Add proper error handling for API calls
- [ ] Implement retry mechanisms
- [ ] Replace print statements with logging
- [ ] Add error reporting

### Documentation Updates
- [ ] Update README.md with latest changes
- [ ] Add API documentation
- [ ] Add contribution guidelines
- [ ] Add development setup guide
 - [ ] Document helper scripts and their diagnostic purpose

## Completed

- [x] Run tests and fix fallout (40 tests passed)