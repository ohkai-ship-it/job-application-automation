# Job Application Automation - Todo List

## In Progress

- None at the moment.

## Not Started

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

## Completed

- Helper Scripts Audit: consolidated helpers and added diagnostics CLI
- Environment Variable Cleanup: centralized config and validation
- Code Organization: type hints, moved helpers to `src/utils`, and module renames
- Test Coverage: broad unit/integration coverage across scraper, trello, cover letter, docx/pdf, and app
- Error Handling & Logging: centralized retries, structured logging, and error reporting with `/errors`
- Documentation: README, API, CONTRIBUTING, DEVELOPMENT, and Helpers docs
- Release v0.1.0: tagged and notes prepared