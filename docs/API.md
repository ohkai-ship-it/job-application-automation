# API Documentation

This document summarizes the public APIs: Python module contracts and Flask endpoints.

## Flask endpoints

- GET `/`  
  Returns the HTML UI.

- POST `/process`  
  Starts a background job to process a Stepstone URL.
  - Request JSON: `{ "url": "https://..." }`
  - Response JSON: `{ "job_id": "<id>", "status": "queued" }`

- GET `/status/<job_id>`  
  Returns status for a previously enqueued job.
  - Response JSON: `{ "job_id": "<id>", "status": "running|done|error", "result": { ... } }`

- GET `/download/<path>`  
  Downloads a generated artifact (TXT/DOCX/PDF).

- GET `/errors`  
  Returns a list of recent error events (sanitized).

## Python modules

### src/scraper.py
- Contract:
  - Input: `url: str`
  - Output: `job_data: dict` with keys like `company_name`, `job_title`, `job_description`, `company_address`, `location`, `source_url`.
- Functions:
  - `scrape_job(url: str) -> dict | None`: returns normalized `job_data` or `None` on unrecoverable error.
  - `save_to_json(job_data: dict, filename: str | None = None) -> str`: save a snapshot to `data/` with timestamped name; returns file path.
- Notes:
  - Prefers JSON-LD extraction, falls back to DOM.
  - Uses centralized HTTP retry helper for polite network behavior.

### src/trello_connect.py
- Contract:
  - Input: `job_data: dict`
  - Output: `dict | None` with keys `{'id': str, 'shortUrl': str, 'already_exists': bool}` (None on failure, with log)
- Class:
  - `TrelloConnect(requester=None)`: requester defaults to `utils.http.request_with_retries`. Inject a fake for tests.
  - `create_card_from_job_data(job_data: dict) -> dict | None`: creates a card with structured layout, labels, and custom fields.
- Card Layout:
  - **Card Name Format:** `[Company] Title (Location)` (uses `job_title_clean` if available)
  - **Card Description:** Rich markdown with sections:
    - Key facts (title, company, location, work mode, language, seniority)
    - Source & IDs (Stepstone ID, company reference)
    - Job description excerpt (300 chars)
    - Company address and links
  - **Idempotency:** Checks existing cards by name and source URL; returns existing card if found
- Automatic Enrichment:
  - **Language Detection:** Word frequency analysis (DE/EN based on common word counts)
  - **Seniority Detection:** Pattern matching (junior/mid/senior/lead keywords in title/description)
  - **Work Mode Normalization:** Maps to remote/hybrid/onsite
- Label Mapping (automatic based on enriched fields):
  - Work mode: `TRELLO_LABEL_REMOTE`, `TRELLO_LABEL_HYBRID`, `TRELLO_LABEL_ONSITE`
  - Language: `TRELLO_LABEL_DE`, `TRELLO_LABEL_EN`
  - Seniority: `TRELLO_LABEL_JUNIOR`, `TRELLO_LABEL_MID`, `TRELLO_LABEL_SENIOR`, `TRELLO_LABEL_LEAD`
- Custom Fields (best-effort, non-fatal):
  - **Text fields (120 char max):**
    - `TRELLO_FIELD_FIRMENNAME` ← `company_name`
    - `TRELLO_FIELD_ROLLENTITEL` ← `job_title_clean` or `job_title`
    - `TRELLO_FIELD_FIRMA_PERSON` ← "Für Arbeitgeber" (constant)
  - **List/dropdown fields:**
    - `TRELLO_FIELD_QUELLE` ← Set to `TRELLO_FIELD_QUELLE_STEPSTONE` option for Stepstone URLs
  - **Date fields:**
    - `TRELLO_FIELD_AUSSCHREIBUNGSDATUM` ← `publication_date` (ISO 8601 format)
- Key Methods:
  - `_enrich_job_data(job_data) -> dict`: Detects and normalizes language/seniority/work_mode
  - `_build_card_name(job_data) -> str`: Formats card name
  - `_build_card_description(job_data) -> str`: Builds markdown description
  - `_get_label_ids(job_data) -> list`: Collects applicable label IDs
  - `_check_existing_card(card_name, source_url) -> str | None`: Checks for duplicates
  - `_set_custom_fields(card_id, job_data) -> None`: Best-effort custom field population
- Notes:
  - See `docs/TRELLO_CARD_LAYOUT.md` for complete feature documentation
  - Use `python -m src.helper.cli trello-inspect` to view board labels and custom fields
  - Use `python generate_trello_config.py` to extract field IDs from your board

### src/cover_letter.py
- Contract:
  - Input: `job_data: dict`, optional `target_language: str` ("de"|"en")
  - Output: `text: str` (cover letter, 180–240 words)
- Class:
  - `CoverLetterGenerator()` with methods:
    - `detect_language(job_data) -> str`
    - `detect_seniority(job_data) -> str`
    - `generate_cover_letter(job_data, target_language=None) -> str`
    - `save_cover_letter(text, job_data, output_dir=None) -> str`
- Notes:
  - Enforces 180–240 words; raises `AIGenerationError` on violations.
  - Loads CV PDFs from `data/`.

### src/docx_generator.py
- Contract:
  - Input: `cover_letter_text: str`, `job_data: dict`, `filename: str`, `language: str`
  - Output: Path to generated DOCX
- Functions:
  - `generate_from_template(...) -> str`
  - `convert_to_pdf(docx_path) -> str | None`
- Notes:
  - Supports placeholder replacement across runs and in tables.
  - Falls back to a basic layout when template missing.

### src/pdf_generator.py
- Contract:
  - Input: `cover_letter_text: str`, `job_data: dict`, `filename: str`
  - Output: Path to generated PDF
- Notes:
  - Simple styled PDF output using reportlab.

### src/utils/error_reporting.py
- `report_error(message: str, exc: Exception | None = None, context: dict | None = None, severity: str = 'error') -> str`
  - Writes sanitized JSON to `output/errors` with UTC timestamp; returns file path.

### src/utils/http.py
- `request_with_retries(method, url, **kwargs) -> requests.Response`
  - Retries on 429/5xx with backoff; short-circuits non-retryable HTTPError.

### Data shapes
- `job_data` (canonical):
  - `company_name: str | None`
  - `job_title: str | None`
  - `job_title_clean: str | None` (gender markers removed)
  - `job_description: str | None`
  - `company_address: str | None` (combined address)
  - `company_address_line1: str | None`
  - `company_address_line2: str | None`
  - `location: str | None`
  - `work_mode: str | None` (normalized to "remote"|"hybrid"|"onsite")
  - `language: str | None` (auto-detected "DE"|"EN")
  - `seniority: str | None` (auto-detected "junior"|"mid"|"senior"|"lead")
  - `source_url: str`
  - `stepstone_job_id: str | None`
  - `company_job_reference: str | None`
  - `publication_date: str | None` (ISO 8601 format)
  - `career_page_link: str | None`
  - `direct_apply_link: str | None`
  - plus other optional fields for references/metadata.
