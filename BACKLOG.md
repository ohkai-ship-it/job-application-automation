# Backlog (Nice to have)

Items here are deferred for later. Use the issue template to raise them as GitHub issues when ready.

## Diagnostics CLI

1) Batch scrape subcommand
- Summary: Add `batch-scrape` subcommand to run multiple URLs from a file (one per line) and summarize outcomes.
- Acceptance criteria:
  - `python -m src.helper.cli batch-scrape --file urls.txt` processes all valid lines
  - Basic progress and a final summary table (success/failure per URL)
  - Reuses `main.process_job_posting` and existing utils (HTTP retries, reporter)

2) Debug template subcommand
- Summary: Add `debug-template` subcommand to load DOCX template and validate placeholders.
- Acceptance criteria:
  - Reports missing placeholders (e.g., `{{COVER_LETTER_BODY}}`)
  - Lists table cells with placeholders and split placeholder cases
  - Works even if the template is minimal or missing (returns actionable message)

Notes
- Both are optional and low priority; do not block core flows.
- Prefer reusing existing modules and avoiding new dependencies.
