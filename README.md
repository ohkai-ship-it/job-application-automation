# Job Application Automation

Automates the job application process by:
- Scraping job postings from Stepstone
- Creating Trello cards for tracking applications
- Generating personalized cover letters using AI
- Converting cover letters to DOCX and PDF formats

## Setup

1. Clone the repository:
```powershell
git clone https://github.com/YOUR_USERNAME/job-application-automation.git
cd job-application-automation
```

2. Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `config/.env.example` to `config/.env`
- Fill in your API keys and credentials

## Usage

### Web Interface
```powershell
python src/app.py
# Open http://localhost:5000 in your browser
```

### Command Line
```powershell
# Process single URL
python src/main.py https://www.stepstone.de/...

# Process multiple URLs
python src/main.py url1 url2 url3
```

## Development

1. Create a feature branch:
```powershell
git checkout develop
git checkout -b feature/your-feature-name
```

2. Make changes and commit:
```powershell
git add .
git commit -m "Description of your changes"
```

3. Push changes:
```powershell
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub from your feature branch to `develop`