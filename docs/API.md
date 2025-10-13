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
  - Output: `card_url: str | None` (None on failure, with log)
- Class:
  - `TrelloConnect(requester=None)`: requester defaults to `utils.http.request_with_retries`. Inject a fake for tests.
  - `create_card_from_job_data(job_data: dict) -> str | None`: creates a card, sets custom fields and labels.

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
  - `job_description: str | None`
  - `company_address: str | None`
  - `location: str | None`
  - `source_url: str`
  - plus optional fields for references/metadata.
