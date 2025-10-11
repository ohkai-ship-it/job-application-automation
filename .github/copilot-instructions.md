This repository automates job applications: it scrapes Stepstone job postings, creates Trello cards, and generates cover letters (TXT, DOCX, PDF).

How this project is structured (big picture)
- `src/main.py` - Orchestrates the end-to-end workflow (scrape → Trello → AI cover letter → DOCX → PDF). Use this to understand the overall flow.
- `src/scraper.py` - Single-responsibility scraper for Stepstone pages. Outputs a normalized `job_data` dict (keys: `company_name`, `job_title`, `job_description`, `company_address`, `location`, `source_url`, etc.). Prefer JSON-LD extraction; fallback to DOM selectors.
- `src/trello_manager.py` - Encapsulates Trello API interactions. Creates cards, sets custom fields and labels, copies checklists from a template card. Credentials/IDs are read from `config/credentials.env` (but currently hardcoded fallbacks exist).
- `src/trello_manager.py` - Encapsulates Trello API interactions. Creates cards, sets custom fields and labels, copies checklists from a template card. Credentials/IDs are read from `config/.env` (but currently hardcoded fallbacks exist).
- `src/cover_letter_ai.py` - Wraps OpenAI usage: loads CV PDFs (`data/cv_de.pdf`, `data/cv_en.pdf`), builds strict prompts (EN/DE) and enforces 180–240 words. The class exposes `generate_cover_letter`, `detect_language`, `detect_seniority`, and `save_cover_letter`.
- `src/docx_generator.py` and `src/pdf_generator.py` - Convert AI text to `.docx` using templates and to styled PDFs. `docx` templating uses placeholders like `{{COVER_LETTER_BODY}}` and preserves runs.
- `src/app.py` - Optional Flask web UI that runs `process_job_posting` in a background thread and exposes `/process`, `/status/<job_id>`, `/download/<path>` endpoints.

Important conventions & patterns (do not invent alternatives without checking these files)
- job_data canonical shape: inspect `scraper.py` to see exact keys. Tools should consume/produce this dict.
- Use `save_to_json(job_data, filename)` in `scraper.py` for persisted samples. Filenames follow `data/scraped_job_{timestamp}.json`.
- Language detection is heuristic (word-count-based). When generating text prefer passing detected language into `CoverLetterGenerator.generate_cover_letter(job_data, target_language)`.
- Cover-letter length is strictly enforced in prompts (180–240 words). If you change prompt instructions, also update downstream length checks in `cover_letter_ai.py`.
- Docx templates are expected under `data/template_de.docx` and `data/template_en.docx`. If missing, `WordCoverLetterGenerator` falls back to a basic generated layout.
- PDF conversion uses `docx2pdf` (Windows) or manual export. `docx_generator.convert_to_pdf` prints instructions when conversion is not available.

Credentials, secrets, and environment
- Primary credential locations (discoverable): `config/.env` (the repo now stores credentials there). Note some modules still load root `.env`—either export the vars to the environment or keep a `config/.env` and update modules accordingly. However: several modules currently include hardcoded API keys/tokens as fallbacks (search `openai`/`api_key`, `TRELLO_KEY`, `api_key` in `src/`).
- When automating or running tests, ensure `config/.env` contains TRELLO_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID, TRELLO_LIST_ID_LEADS, and optionally template card ids. `cover_letter_ai.py` expects an OpenAI API key (ENV `OPENAI_API_KEY`) unless modified.

Developer workflows & quick commands (Windows PowerShell)
- Run interactive CLI (step-by-step):
  ```powershell
  python src/main.py
  ```
- Run for one or more URLs from CLI:
  ```powershell
  python src/main.py https://...single-url...
  python src/main.py url1 url2 url3
  ```
- Start web UI (Flask):
  ```powershell
  python src/app.py
  # then open http://localhost:5000
  ```
- Run a module-level test/snippet: each module includes a `if __name__ == '__main__'` test that prints what it does. Use these for quick verification (e.g., `python src/scraper.py`).

Integration & external dependencies
- HTTP scraping: `requests`, `beautifulsoup4`, `lxml` (see `src/scraper.py`). Respect polite scraping: `main.batch_process_urls` sleeps 3 seconds between requests.
- OpenAI: `openai` (wrapped by `openai.OpenAI` in `cover_letter_ai.py`) and `pypdf` to read CV PDFs. The code currently uses `OpenAI(api_key=...)` constructor.
- Trello: direct REST calls to Trello API (see `src/trello_manager.py`). Custom field and label IDs are repository-specific; changing board layout requires updating IDs.
- DOCX/PDF: `python-docx` (`docx`) for templates, `docx2pdf` (optional, Windows) for conversion, and `reportlab` for styled PDFs.

Project-specific gotchas / signals an AI should watch for
- Hardcoded secrets: code contains hardcoded keys (temporary). Do not output or replicate those values in generated content. If you modify credentials, update `config/.env` rather than editing source.
- Prompt/word-count coupling: prompts require EXACT word counts; generated text is validated for length after the API call. Avoid changing one side only.
- Template placeholders: `{{COVER_LETTER_BODY}}`, `{{SENDER_NAME}}`, etc. Replacements preserve run-level formatting. Use `_replace_in_paragraph` in `docx_generator.py` as reference.
- Trello custom-field IDs and label IDs are tightly coupled to the Trello board. Use `_load_dropdown_options` in `trello_manager.py` to map human-friendly options where possible.
- The scraper prioritizes JSON-LD. If adding new site parsers, follow the `job_data` shape and reuse `save_to_json` for persisted examples.

Examples from code (use these for context when writing new code)
- Create card: `TrelloManager.create_card_from_job_data(job_data)` used by `src/main.py`.
- Generate cover letter: `CoverLetterGenerator().generate_cover_letter(job_data)` and `save_cover_letter(cover_letter, job_data)` save a `.txt` file to `output/cover_letters/`.
- DOCX generation: `WordCoverLetterGenerator().generate_from_template(cover_letter_text, job_data, docx_filename, language=language)` then `convert_to_pdf`.

Quality gates
- Quick local checks:
  - Lint/typing: project has no explicit config; run your typical linters locally if required.
  - Run module tests (each module has manual test stubs): `python src/scraper.py`, `python src/trello_manager.py`, etc.

If anything in these notes is unclear or you want me to surface more specific patterns (example JSON outputs, common failure modes, or a checklist for safely rotating credentials), tell me which area to expand and I'll update this file.
