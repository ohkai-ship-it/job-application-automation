Helper Scripts Guide

Purpose: these scripts are diagnostics or ad-hoc inspectors. Prefer the main modules for production flows.

- src/helper/inspect_html.py
  - Reuses utils.html to parse and introspect HTML, list headers, data-at elements, JSON-LD blocks, and keyword hits.
  - Usage: python src/helper/inspect_html.py [reads data/debug_page.html by default]

- src/helper/test_trello_auth.py
  - Minimal Trello auth probe. Reads credentials via utils.env/utils.trello; prints masked key/token and basic profile info.
  - Intended for diagnostics only. Prefer TrelloConnect and its tests for automation.

- src/helper/trello_inspector.py
  - Board explorer: lists board info, lists, labels, custom fields, and optional template card details using utils.trello auth.
  - Diagnostics only; do not embed in automation flows.

- src/helper/batch_scraper_test.py
  - Batch-scrapes a fixed list of Stepstone URLs with polite delays; writes JSONs to data/ and a summary file.
  - For manual testing of scraper robustness; production flows should use src/main.py or tests.

- src/helper/debug_template.py
  - Analyzes a Word template’s paragraphs/runs/tables to help debug placeholder splitting.
  - Use tests in tests/unit/test_docx_generator_more.py for automated checks.

Refactor notes
- Overlap with utils:
  - HTML parsing/search lives in src/utils/html.py and is used by inspect_html.py.
  - Trello auth handling lives in src/utils/trello.py and is used by trello_inspector.py and test_trello_auth.py.
  - HTTP retry logic lives in src/utils/http.py and is used by main modules; helpers do not implement their own retries.

Recommendations
- Keep helper scripts as diagnostics; avoid side effects in production.
- For future: wrap helpers under a CLI entrypoint and mark them clearly as diagnostics.
