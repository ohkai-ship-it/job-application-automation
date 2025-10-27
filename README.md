# Job Application Automation

> Automate your job search. Scrape job postings  Create Trello cards  Generate AI cover letters  Export to DOCX/PDF

A Python tool that transforms the tedious job application process into an efficient workflow.

## Features

- Scrape job postings from Stepstone & LinkedIn
- Create Trello cards with intelligent fields
- Generate AI cover letters (180-240 words)
- Export to DOCX/PDF with professional templates  
- Web UI for batch processing

## Quick Start

See SETUP_GUIDE.md for complete setup (20-30 minutes).

TL;DR:
\\\powershell
git clone https://github.com/ohkai-ship-it/job-application-automation.git
cd job-application-automation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env with credentials
python src/main.py https://www.stepstone.de/...
\\\

## Documentation

- SETUP_GUIDE.md - Complete setup
- CONTRIBUTING.md - How to contribute
- docs/DEVELOPMENT.md - Dev workflow
- docs/TRELLO_CARD_LAYOUT.md - Card structure
- BACKLOG.md - Feature roadmap
- CHANGELOG.md - Release history

## Usage

### Command Line
\\\powershell
python src/main.py https://...
python src/main.py url1 url2 url3
\\\

### Web UI
\\\powershell
python src/app.py
# Open http://localhost:5000
\\\

### Diagnostics
\\\powershell
python -m src.utils.cli trello-auth
python -m src.utils.cli trello-inspect
python -m src.utils.cli inspect-html --file data/debug_page.html
\\\

## Development

\\\powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
\\\

See CONTRIBUTING.md for guidelines.

## Project Structure

\\\
src/main.py - Orchestrates workflow
src/scraper.py - Stepstone scraper
src/linkedin_scraper.py - LinkedIn scraper
src/trello_connect.py - Trello API
src/cover_letter.py - AI generation
src/docx_generator.py - DOCX export
src/pdf_generator.py - PDF export
src/app.py - Flask UI
src/utils/ - Utilities and CLI
tests/ - Test suite
docs/ - Documentation
data/ - CV files and templates
output/ - Generated files
\\\

## Security

- No secrets in repo (use config/.env)
- CV files local only
- Error logs sanitized
- Template flexibility (personal signatures locally, public placeholders on GitHub)

## License

MIT - see LICENSE

## Support

- Questions? Check docs or open an issue
- Bug reports? Include steps to reproduce  
- Ideas? See BACKLOG.md for planned features

Happy job hunting!
