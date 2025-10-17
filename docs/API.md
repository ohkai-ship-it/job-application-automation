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
  - Output: `text: str` (cover letter body, 180–240 words)
  - Side effect: Adds `cover_letter_salutation`, `cover_letter_body`, `cover_letter_valediction` to `job_data`
- Class:
  - `CoverLetterGenerator()` with methods:
    - `detect_language(job_data) -> str`: Auto-detect DE/EN from job description word frequency
    - `detect_seniority(job_data) -> str`: Pattern matching for junior/mid/senior/lead/executive
    - `detect_german_formality(job_description) -> str`: Analyzes du vs. Sie pronouns; returns 'informal' or 'formal'
    - `generate_salutation(job_data, language, formality, seniority) -> str`: Context-aware greeting
      - Uses contact person name if available (detects gender from Herr/Frau)
      - Falls back to generic team greeting
      - Matches tone to seniority level
    - `generate_valediction(language, formality, seniority) -> str`: Appropriate closing
      - German formal: "Mit freundlichen Grüßen"
      - German informal: "Viele Grüße" (junior/mid) or "Beste Grüße" (senior+)
      - English: "Sincerely" (exec/senior formal) or "Best" (informal) or "Best regards" (default)
    - `generate_cover_letter(job_data, target_language=None) -> str`: Orchestrates full generation
      1. Detects language and seniority
      2. Detects formality (for German)
      3. Generates salutation
      4. Calls OpenAI for body text (with formality instruction for German)
      5. Generates valediction
      6. Stores all three parts in `job_data` dict
      7. Returns body text (for backward compatibility)
    - `save_cover_letter(text, job_data, output_dir=None) -> str`: Saves body to TXT file
- Three-Part Structure:
  - `job_data['cover_letter_salutation']`: Personalized or generic greeting
  - `job_data['cover_letter_body']`: AI-generated 180–240 word body
  - `job_data['cover_letter_valediction']`: Tone-matched closing
- Notes:
  - Enforces 180–240 words on body text; raises `AIGenerationError` on violations
  - Loads CV PDFs from `data/cv_de.pdf` and `data/cv_en.pdf`
  - German formality detection uses pronoun counting (weights capitalized "Sie" heavily)
  - AI prompt includes formality instructions for German: "Verwende die Du-Form" or "Verwende die Sie-Form"

### src/docx_generator.py
- Contract:
  - Input: `cover_letter_text: str`, `job_data: dict`, `filename: str`, `language: str`
  - Output: Path to generated DOCX
- Functions:
  - `generate_from_template(...) -> str`
  - `convert_to_pdf(docx_path) -> str | None`
- Template Placeholders:
  - `{{COVER_LETTER_BODY}}`: Main cover letter text (AI-generated)
  - `{{COVER_LETTER_SALUTATION}}`: Personalized/generic greeting
  - `{{COVER_LETTER_VALEDICTION}}`: Tone-matched closing
  - Plus other standard placeholders: `{{COMPANY_NAME}}`, `{{JOB_TITLE}}`, etc.
- Notes:
  - Supports placeholder replacement across runs and in tables
  - Falls back to a basic layout when template missing
  - Templates expected at `data/template_de.docx` and `data/template_en.docx`

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
  - `contact_person: dict | None` with key `name: str` (contact person's full name)
  - `cover_letter_salutation: str | None` (added by `CoverLetterGenerator.generate_cover_letter`)
  - `cover_letter_body: str | None` (added by `CoverLetterGenerator.generate_cover_letter`)
  - `cover_letter_valediction: str | None` (added by `CoverLetterGenerator.generate_cover_letter`)
  - plus other optional fields for references/metadata.
