# Job Application Automation - Todo List

## In Progress

- None at the moment.

## Not Started

### Critical (Before Production)
- [ ] **ACTIVATE DUPLICATE DETECTION**: Change `src/main.py` Step 0 to stop processing on duplicates (currently warns but continues for easier testing)
- [ ] **TIGHTEN COVER LETTER VALIDATION**: Change `src/cover_letter.py` word count validation from 170-250 to strict 180-240 (currently relaxed for testing)

### Next Milestone (v0.1.x)
- [ ] Merge feature/infrastructure-setup into develop/main and publish GitHub Release for v0.1.0 (use docs/RELEASE_NOTES_v0.1.0.md)
- [ ] Retire legacy names cleanly
    - [ ] Remove or add shims with deprecation warnings for old modules (trello_manager.py, cover_letter_ai.py)
- [ ] CI & Guardrails
    - [ ] Add GitHub Actions workflow to run `pytest -q` on Windows and Ubuntu
    - [ ] Optional: pre-commit hooks (black, isort, ruff)
- [ ] Hygiene & safety
    - [ ] Enable secret scanning/gitleaks; verify no hardcoded secrets
    - [ ] Add basic branch protection rules for develop/main
- [ ] README polish
    - [ ] Add a short Table of Contents
    - [ ] Add a "Known limitations" section (Stepstone-only, template expectations, docx2pdf availability)

### Future Enhancements (Nice-to-Have)
- [ ] **Trello Card Location/Map Feature**: Implement reliable location mapping
    - Current issue: Trello's geocoding via API is unreliable (sometimes works, sometimes doesn't)
    - Attempted approaches:
      - Setting `address` and `locationName` with "City, Deutschland" format
      - Trello requires coordinates for map display, but geocoding is inconsistent
    - Possible solutions to explore:
      - Use a geocoding service (Google Maps API, Nominatim) to get coordinates before sending to Trello
      - Maintain hardcoded coordinates dictionary for common German cities
      - Wait for Trello API improvements
    - Code: `_set_card_location()` method exists but is currently disabled in `trello_connect.py`
- [ ] **Attachments Reliability**: Investigate timeout issues with Trello attachments API
    - Current issue: Attachment API calls frequently timeout (10s timeout)
    - May need to increase timeout or implement async/background attachment uploads

## Completed

- Helper Scripts Audit: consolidated helpers and added diagnostics CLI
- Environment Variable Cleanup: centralized config and validation
- Code Organization: type hints, moved helpers to `src/utils`, and module renames
- Test Coverage: broad unit/integration coverage across scraper, trello, cover letter, docx/pdf, and app
- Error Handling & Logging: centralized retries, structured logging, and error reporting with `/errors`
- Documentation: README, API, CONTRIBUTING, DEVELOPMENT, and Helpers docs
- Release v0.1.0: tagged and notes prepared