# 📋 Backlog

Nice-to-have features and improvements for future versions. These are lower priority than the core workflow but would enhance the tool.

## Platform Support

### XING Integration
- **Priority**: Medium  
- **Effort**: High (~3 days)
- **Description**: Add support for XING job postings (German/Swiss market)
- **Requirements**:
  - JSON-LD extraction (if available) or DOM-based parsing
  - Reuse existing job_data normalization
  - Follow same language/seniority detection patterns

### Indeed Integration
- **Priority**: Medium  
- **Effort**: High (~3 days)
- **Description**: Add support for Indeed job postings (large global platform)
- **Requirements**:
  - Handle dynamic content via Playwright if needed
  - Normalize to job_data schema
  - Test with various locales (en_US, de_DE, etc.)

### LinkedIn Direct Posts
- **Priority**: Low  
- **Effort**: High (~2 days)
- **Description**: Scrape LinkedIn job posts directly (not just Collections)
- **Requirements**:
  - May require additional Playwright handling for auth or dynamic content
  - Reuse existing LinkedIn scraper patterns

---

## CLI Enhancements

### Batch Scrape Subcommand
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Add `batch-scrape` subcommand to process multiple URLs from a file
- **Usage**: `python -m src.utils.cli batch-scrape --file urls.txt`
- **Requirements**:
  - Read URLs from text file (one per line)
  - Reuse existing `process_job_posting` logic
  - Display progress table (success/failure count per URL)
  - Respect rate-limiting delays between requests

### Template Debug Tool
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Validate DOCX templates and check for required placeholders
- **Usage**: `python -m src.utils.cli debug-template --file data/template_de.docx`
- **Requirements**:
  - Validate placeholders exist: `{{COVER_LETTER_BODY}}`, `{{SENDER_NAME}}`, etc.
  - List all placeholder locations
  - Report missing required placeholders

### HTML Inspector Enhancements
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Improve the `inspect-html` command with better filtering and export options
- **Requirements**:
  - Add `--output json` flag for structured output
  - Add `--filter` option to search specific content types

---

## Cover Letter Generation

### Template Variations
- **Priority**: Low  
- **Effort**: Medium (~2 days)
- **Description**: Support custom prompt templates for different industries
- **Requirements**:
  - Store templates in `config/prompts/` (tech, management, sales, etc.)
  - Allow users to specify which template to use per job
  - Fallback to default template

### Multi-Language Support Expansion
- **Priority**: Low  
- **Effort**: Medium (~1 day)
- **Description**: Add support for French, Spanish, Italian
- **Requirements**:
  - Extend language detection heuristic
  - Create prompts for new languages
  - Test with job descriptions in each language

---

## UI/UX Improvements

### Web UI Enhancements
- **Priority**: Low  
- **Effort**: Medium (~2-3 days)
- **Description**: Improve Flask web UI with better feedback and error handling
- **Features**:
  - Real-time job processing progress (WebSocket or polling)
  - Downloadable batch job reports (CSV)
  - Job posting preview before processing
  - Settings editor for template selection, language, etc.

### Browser Extension
- **Priority**: Very Low  
- **Effort**: Very High (~5-7 days)
- **Description**: Create browser extension to auto-capture job URLs from job boards
- **Requirements**:
  - Chrome/Firefox extension manifests
  - One-click URL capture and send to local server
  - Requires running local Flask app

---

## Data & Analytics

### Job Application Tracking
- **Priority**: Low  
- **Effort**: Medium (~2-3 days)
- **Description**: Track applications over time (sent date, responses, interviews scheduled)
- **Requirements**:
  - Extend Trello card fields with status tracking
  - Optional: Export statistics to CSV/JSON
  - Track rejection/offer/interview rates

### Search Analytics
- **Priority**: Very Low  
- **Effort**: Low (~1 day)
- **Description**: Generate reports on job search (top companies, locations, salary ranges)
- **Requirements**:
  - Analyze scraped job_data over time
  - Export summary statistics

---

## Performance & Reliability

### Caching Layer
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Cache scraped job data to avoid re-scraping duplicate URLs
- **Requirements**:
  - Store job_data in SQLite with content hash
  - Skip processing if URL hash matches cached job

### Retry Logic Improvements
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Enhanced retry strategies for API failures
- **Requirements**:
  - Exponential backoff for OpenAI rate limiting
  - Better error messages for Trello API failures

### Parallel Processing
- **Priority**: Very Low  
- **Effort**: High (~2 days)
- **Description**: Process multiple job URLs concurrently (currently sequential)
- **Requirements**:
  - Thread pool or async/await refactor
  - Handle rate limiting across concurrent requests
  - Careful with OpenAI API quotas

---

## Documentation

### Video Tutorials
- **Priority**: Very Low  
- **Effort**: High (~4-5 hours)
- **Description**: Record setup and usage videos
- **Topics**:
  - 5-minute setup guide
  - Platform-specific scraping examples
  - Trello board configuration

### API Documentation
- **Priority**: Low  
- **Effort**: Low (~1 day)
- **Description**: Expand OpenAPI/Swagger docs for Flask app
- **Requirements**:
  - Add interactive API explorer
  - Document all endpoints with examples

---

## Notes

- **Prioritization**: Use "Priority" and "Effort" to decide which features to tackle first
- **Contributing**: If you'd like to implement any of these, see **[CONTRIBUTING.md](CONTRIBUTING.md)**
- **Discussions**: Open an issue to discuss scope or suggest alternatives
