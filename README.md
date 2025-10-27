# 🚀 Job Application Automation# 🚀 Job Application Automation



> **Automate your job search.** Scrape job postings → Create Trello cards → Generate AI cover letters → Export to DOCX/PDF> **Automate your job search.** Scrape job postings → Create Trello cards → Generate AI cover letters → Export to DOCX/PDF



A Python tool that transforms the tedious job application process into an efficient workflow. One URL → automated pipeline → professional cover letter, Trello card, and export-ready documents.A Python tool that transforms the tedious job application process into an efficient workflow. One URL → automated pipeline → professional cover letter, Trello card, and export-ready documents.



---



## ✨ What It Does## ✨ What It Does## ✨ What It Does



- 🔍 **Scrape job postings** from Stepstone & LinkedIn  

- 🗂️ **Create Trello cards** with intelligent fields (language, seniority, work mode)  

- ✍️ **Generate AI cover letters** (180–240 words, bilingual, personalized)  🔍 **Scrape job postings** from Stepstone & LinkedIn  🔍 **Scrape job postings** from Stepstone & LinkedIn  

- 📄 **Export to DOCX/PDF** using professional templates  

- 🌐 **Web UI** for batch processing with background jobs  🗂️ **Create Trello cards** with custom fields and labels  🗂️ **Create Trello cards** with custom fields and labels  



---✍️ **Generate AI cover letters** (180–240 words, DE/EN, personalized)  ✍️ **Generate AI cover letters** (180–240 words, DE/EN, personalized)  



## ⚡ Quick Start📄 **Export to DOCX/PDF** using professional templates  📄 **Export to DOCX/PDF** using professional templates  



### 👉 Recommended: Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)🌐 **Web UI** for batch processing with background jobs  🌐 **Web UI** for batch processing with background jobs  

Complete step-by-step setup (20-30 minutes)



### ⏱️ TL;DR for experienced users

## 🚀 Get Started in 3 Minutes## 🚀 Get Started in 3 Minutes

```powershell

git clone https://github.com/ohkai-ship-it/job-application-automation.git

cd job-application-automation

python -m venv .venv### Option 1: Complete Setup (Recommended)### Option 1: Quick Setup (Recommended)

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt👉 **[Follow SETUP_GUIDE.md](SETUP_GUIDE.md)** (20-30 minutes, step-by-step)👉 **[Follow SETUP_GUIDE.md](SETUP_GUIDE.md)** (20-30 minutes, step-by-step)



# Copy and configure credentials

cp config/.env.example config/.env

# Edit config/.env with your TRELLO_KEY, TRELLO_TOKEN, OPENAI_API_KEY### Option 2: TL;DR for experienced users### Option 2: TL;DR for experienced users



# Test with a single job posting URL```powershell```powershell

python src/main.py https://www.stepstone.de/e/...

```git clone https://github.com/ohkai-ship-it/job-application-automation.gitgit clone https://github.com/ohkai-ship-it/job-application-automation.git



Check results in:cd job-application-automationcd job-application-automation

- **Cover letter**: `output/cover_letters/`

- **Trello board**: New card automatically createdpython -m venv .venvpython -m venv .venv

- **DOCX/PDF**: `output/`

.\.venv\Scripts\Activate.ps1.\.venv\Scripts\Activate.ps1

---

pip install -r requirements.txtpip install -r requirements.txt

## 🎯 Supported Platforms

# Copy config/.env.example to config/.env and fill in credentials# Copy config/.env.example to config/.env and fill in credentials

| Platform | Status | Notes |

|----------|--------|-------|python src/main.py https://www.stepstone.de/...python src/main.py https://www.stepstone.de/...

| **Stepstone** | ✅ v0.1 | Stable (JSON-LD extraction) |

| **LinkedIn** (Collections) | ✅ v0.1 | Full JS rendering via Playwright |``````

| LinkedIn (Direct) | 📋 v0.2 | Planned |

| XING | 📋 Future | Planned |

| Indeed | 📋 Future | Planned |

Then check:Then check:

---

- Generated cover letter: `output/cover_letters/`- Generated cover letter: `output/cover_letters/`

## 📖 Documentation

- Trello board: New card created- Trello board: New card created

**Getting Started:**

- 👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** – Complete setup instructions- DOCX/PDF: `output/`- DOCX/PDF: `output/`

- **[CONTRIBUTING.md](CONTRIBUTING.md)** – How to contribute



**Technical Reference:**

- **[docs/SCRAPER_ARCHITECTURE.md](docs/SCRAPER_ARCHITECTURE.md)** – Architecture & roadmap## 🎯 Supported Platforms## 🎯 Supported Platforms

- **[docs/TRELLO_CARD_LAYOUT.md](docs/TRELLO_CARD_LAYOUT.md)** – Card structure & fields

- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** – Dev workflow & testing

- **[docs/API.md](docs/API.md)** – API reference

| Platform | Status | Notes || Platform | Status | Notes |

**Project Info:**

- **[BACKLOG.md](BACKLOG.md)** – Feature roadmap|----------|--------|-------||----------|--------|-------|

- **[CHANGELOG.md](CHANGELOG.md)** – Release history

| **Stepstone** | ✅ v0.1 | Stable, JSON-LD extraction || **Stepstone** | ✅ v0.1 | Stable, JSON-LD extraction |

---

| **LinkedIn** (Collections) | ✅ v0.1 | Full JS rendering via Playwright || **LinkedIn** (Collections) | ✅ v0.1 | Full JS rendering via Playwright |

## 💻 Usage

| LinkedIn (Direct) | 📋 v0.2 | Planned || LinkedIn (Direct) | 📋 v0.2 | Planned |

### Command Line

| XING | 📋 Future | Planned || XING | 📋 Future | Planned |

```powershell

# Single URL| Indeed | 📋 Future | Planned || Indeed | 📋 Future | Planned |

python src/main.py https://www.stepstone.de/...



# Multiple URLs (auto-detects platform)

python src/main.py url1 url2 url3## 📖 Documentation## 📖 Documentation



# Interactive mode (step-by-step)

python src/main.py

```**For setup & installation:****For setup & installation:**



### Web UI- 👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** – Complete setup (20-30 min)- 👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** – Complete setup (20-30 min)



```powershell- **[CONTRIBUTING.md](CONTRIBUTING.md)** – How to contribute- **[CONTRIBUTING.md](CONTRIBUTING.md)** – How to contribute

python src/app.py

# Open http://localhost:5000 in your browser

```

**For technical details:****For technical details:**

### Diagnostics

- **[docs/SCRAPER_ARCHITECTURE.md](docs/SCRAPER_ARCHITECTURE.md)** – Roadmap & architecture- **[docs/SCRAPER_ARCHITECTURE.md](docs/SCRAPER_ARCHITECTURE.md)** – Roadmap & architecture

```powershell

# Test Trello connection- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** – Development workflow- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** – Development workflow

python -m src.utils.cli trello-auth

- **[docs/TRELLO_CARD_LAYOUT.md](docs/TRELLO_CARD_LAYOUT.md)** – Card structure- **[docs/TRELLO_CARD_LAYOUT.md](docs/TRELLO_CARD_LAYOUT.md)** – Card structure

# View Trello board config (lists, labels, custom fields)

python -m src.utils.cli trello-inspect- **[docs/API.md](docs/API.md)** – API reference- **[docs/API.md](docs/API.md)** – API reference



# Inspect HTML structure and JSON-LD- **[BACKLOG.md](BACKLOG.md)** – Feature roadmap- **[BACKLOG.md](BACKLOG.md)** – Feature roadmap

python -m src.utils.cli inspect-html --file data/debug_page.html

```- **[CHANGELOG.md](CHANGELOG.md)** – Release history- **[CHANGELOG.md](CHANGELOG.md)** – Release history



---



## 🏗️ Features## 🏗️ Features at a Glance## Trello Card Layout



### Smart Job Card Creation

- **Language Detection** – Analyzes job description for DE/EN

- **Seniority Detection** – Identifies junior/mid/senior/lead### Smart Job Card CreationCards are automatically created with intelligent fields:

- **Work Mode Normalization** – Maps to remote/hybrid/onsite

- **Automatic Labels** – Based on detected attributes- **Language Detection** - Analyzes job description for DE/EN- **Language Detection** - Analyzes job description for DE/EN

- **Duplicate Prevention** – Checks by name and source URL

- **Seniority Detection** - Identifies junior/mid/senior/lead- **Seniority Detection** - Identifies junior/mid/senior/lead

### AI Cover Letter Generation

- **Context-Aware** – Uses your CV for personalization- **Work Mode Normalization** - Maps to remote/hybrid/onsite- **Work Mode Normalization** - Maps to remote/hybrid/onsite

- **Bilingual** – Generates in German or English

- **Tone Matched** – Adjusts formality (du/Sie) based on seniority- **Automatic Labels** - Based on detected attributes- **Automatic Labels** - Based on detected attributes

- **Strict Word Count** – Always 180–240 words

- **Custom Signatures** – Uses `{{SENDER_SIGNATURE}}` placeholder- **Duplicate Prevention** - Checks by name and source URL- **Duplicate Prevention** - Checks by name and source URL



### Export Formats

- **DOCX** – Professional Word templates (German & English)

- **PDF** – Styled PDF output### AI Cover Letter GenerationSee `docs/TRELLO_CARD_LAYOUT.md` for complete details.

- **TXT** – Plain text files

- **Context-Aware** - Uses your CV for personalization

---

- **Bilingual** - Generates in German or English## 💻 Usage

## 🔧 Development

- **Tone Matched** - Adjusts formality (du/Sie) and seniority

### Local Setup

- **Strict Word Count** - Always 180–240 words### Command Line

```powershell

# Clone and enter directory- **Custom Signatures** - Template support with {{SENDER_SIGNATURE}}```powershell

git clone https://github.com/ohkai-ship-it/job-application-automation.git

cd job-application-automation# Single URL



# Create virtual environment### Export Formatspython src/main.py https://www.stepstone.de/...

python -m venv .venv

.\.venv\Scripts\Activate.ps1- **DOCX** - Professional Word templates (German & English)



# Install dependencies- **PDF** - Styled PDF output# Multiple URLs (auto-detects platform)

pip install -r requirements.txt

- **TXT** - Plain text filespython src/main.py url1 url2 url3

# Configure environment

cp config/.env.example config/.env```

# Edit config/.env with your credentials

```## 💻 Usage



### Running Tests### Web UI (with background processing)



```powershell### Command Line```powershell

# Using VS Code task (recommended)

# In VS Code: Run Task → "Run tests"```powershellpython src/app.py



# Or directly# Single URL# Open http://localhost:5000

pytest -q

```python src/main.py https://www.stepstone.de/...```



### Contributing



1. **Create a feature branch**# Multiple URLs (auto-detects platform)### Diagnostics

   ```powershell

   git checkout developpython src/main.py url1 url2 url3```powershell

   git checkout -b feature/your-feature-name

   ``````python -m src.helper.cli trello-auth     # Test Trello connection



2. **Make changes and test**python -m src.helper.cli trello-inspect  # View board configuration

   ```powershell

   pytest -q### Web UI (with background processing)python -m src.helper.cli inspect-html --file data/debug_page.html

   ```

```powershell```

3. **Commit and push**

   ```powershellpython src/app.py

   git add .

   git commit -m "Describe your change"# Open http://localhost:5000## Error reporting

   git push origin feature/your-feature-name

   ``````Critical failures are recorded under `output/errors` as sanitized JSON events.



4. **Open a Pull Request** to `develop` branch on GitHub- The Flask app’s global error handler writes events automatically



See **[CONTRIBUTING.md](CONTRIBUTING.md)** for full guidelines.### Diagnostics- The main workflow reports when scraping returns empty data or AI generation fails



---```powershell- No secrets are stored; sensitive keys are masked



## 📁 Project Structurepython -m src.helper.cli trello-auth     # Test Trello connection



```python -m src.helper.cli trello-inspect  # View board configuration## Development

src/

├── main.py                 # Orchestrates scrape → Trello → AI → DOCX → PDFpython -m src.helper.cli inspect-html --file data/debug_page.html

├── scraper.py             # Stepstone scraper

├── linkedin_scraper.py     # LinkedIn scraper```1) Create a feature branch

├── trello_connect.py       # Trello API client

├── cover_letter.py         # AI generation```powershell

├── docx_generator.py       # DOCX generation with templates

├── pdf_generator.py        # PDF export## 🔧 Developmentgit checkout develop

├── app.py                  # Flask web UI

└── utils/                  # Logging, errors, helpers, CLIgit checkout -b feature/your-feature-name

    └── cli.py              # Diagnostics CLI

### Contributing```

tests/                      # Unit & integration tests

docs/                       # Technical documentationWe welcome pull requests! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

config/                     # Configuration templates

data/                       # CV files & templates (user-provided)2) Run tests locally

output/                     # Generated cover letters, DOCX, PDF

```### Quick Start```powershell



---```powershell# Using VS Code task (Windows-safe quoting)



## 🔒 Security & Privacy# Create feature branch# In VS Code: Run Task → "Run tests" (invokes .venv/Scripts/python.exe -m pytest -q)



- **No secrets in repo** – Credentials stored in `config/.env` (excluded from git)git checkout -b feature/your-feature

- **CV files local only** – Your CVs never uploaded or shared

- **Error sanitization** – Sensitive data masked in error logs# Or directly

- **Template flexibility** – Use personal signed versions locally, public templates on GitHub

# Run testspytest -q

---

pytest -q```

## 📜 License



MIT License – see [LICENSE](LICENSE)

# Commit and push3) Commit and push

---

git add .```powershell

## 🤝 Support

git commit -m "Your message"git add .

- **Questions?** Check the docs above or open an issue

- **Found a bug?** Please report it with detailsgit push origin feature/your-featuregit commit -m "Describe your change"

- **Have ideas?** See [BACKLOG.md](BACKLOG.md) for planned features

```git push origin feature/your-feature-name

Happy job hunting! 🎯

```

Then open a Pull Request on GitHub.

4) Open a Pull Request from your branch to `develop` on GitHub

### Project Structure

- `src/main.py` – Orchestrates workflow### Project layout (high level)

- `src/scraper.py` – Stepstone scraper- `src/main.py` – Orchestrates scrape → Trello → AI cover letter → DOCX → PDF

- `src/linkedin_scraper.py` – LinkedIn scraper- `src/scraper.py` – Stepstone scraper. Outputs normalized job_data dict

- `src/trello_connect.py` – Trello API client- `src/linkedin_scraper.py` – LinkedIn scraper (new in v0.1). Outputs same job_data format

- `src/cover_letter.py` – AI generation- `src/trello_connect.py` – Trello API client (card creation, fields, labels)

- `src/app.py` – Flask web UI- `src/cover_letter.py` – AI cover letter generation and save helpers

- `tests/` – Unit & integration tests- `src/docx_generator.py`, `src/pdf_generator.py` – DOCX and PDF generation

- `src/app.py` – Flask web UI

For architecture details, see **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**- `src/utils/*` – Logging, errors, HTML helpers, Trello auth helpers, HTTP retries, error reporting

- `info/HELPERS.md` – Helper scripts audit and usage

## 📜 License- `tests/` – Unit and integration tests



MIT License - see [LICENSE](LICENSE) file### Documentation



---See our documentation for detailed guides:

- **`docs/SCRAPER_ARCHITECTURE.md`** – Future architecture, infrastructure roadmap (Phase 1-4)

**Questions?** See the detailed guides in the [📖 Documentation](#-documentation) section above.- **`docs/RELEASE_NOTES_v0.1.md`** – v0.1 features, known limitations, testing info

- **`docs/TRELLO_CARD_LAYOUT.md`** – Trello card structure and field mappings
- **`docs/DEVELOPMENT.md`** – Development workflow and best practices

## Contributing
We welcome PRs. See CONTRIBUTING.md for guidelines (branching model, testing, code style, and secrets policy).

See also: BACKLOG.md for low-priority, nice-to-have ideas.

## Helpers and diagnostics
See `info/HELPERS.md` for an overview of helper scripts and their diagnostic purpose. Prefer using the Diagnostics CLI (`python -m src.helper.cli ...` or `jobapp-diag ...`) for common tasks like HTML inspection and Trello checks.

## License
MIT (see LICENSE file)
 
 