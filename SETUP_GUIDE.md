# Setup Guide: Job Application Automation

This guide walks you through setting up the Job Application Automation tool on your local machine. The process takes approximately **20-30 minutes**.

## Prerequisites

- **Python 3.10+** (check with `python --version`)
- **Git** installed
- **OpenAI API key** (https://platform.openai.com/api-keys)
- **Trello account** with API access enabled
- **Windows, Mac, or Linux**

## Step 1: Clone the Repository

```powershell
git clone https://github.com/ohkai-ship-it/job-application-automation.git
cd job-application-automation
```

## Step 2: Create Virtual Environment

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Mac/Linux (Bash/Zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Additional Setup for LinkedIn Support

LinkedIn scraping uses Playwright for JavaScript rendering. Install the required browser:

```powershell
playwright install chromium
```

This downloads Chromium (~400MB). Only needed if you plan to scrape LinkedIn job collections.

## Step 4: Prepare Your CV Files

The application uses your CV to generate personalized cover letters. You must provide PDFs in both languages:

1. **German CV:** Place at `data/cv_de.pdf`
2. **English CV:** Place at `data/cv_en.pdf`

**Steps:**
1. Create or export your CV as PDF (Word, Google Docs, or any PDF tool)
2. Copy the German version to `data/cv_de.pdf`
3. Copy the English version to `data/cv_en.pdf`

> **Why both?** The application detects job language and generates cover letters in that language. Your CV should match for consistency.

## Step 5: Set Up OpenAI API Key

### Get Your API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you won't see it again!)
4. **Set billing:** https://platform.openai.com/account/billing/overview (ensure credits or subscription active)

### Cost Estimate

- ~$0.01 per cover letter (using gpt-4-mini)
- Bulk processing 100 jobs = ~$1.00

### Add to Environment

Create `config/.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

## Step 6: Set Up Trello Integration

### 6.1 Get Trello Credentials

1. Go to https://trello.com/app/keys
2. Copy your **API Key**
3. Click "Tokens" → "Create a Token"
4. Copy your **Token** (saves to a safe place)

### 6.2 Create a Trello Board

1. Go to https://trello.com
2. Click "Create new board"
3. Name it (e.g., "Job Applications")
4. Make it **Private** (recommended)

### 6.3 Get Your Board ID

1. Open your board
2. Look at the URL: `https://trello.com/b/ABC123xyz/job-applications`
3. Your Board ID is `ABC123xyz`

### 6.4 Create a "Leads" List

1. In your board, create a new list named "Leads" (or your preferred name)
2. This is where job cards will be created

### 6.5 Get Your List ID

Use the diagnostic CLI to find your list ID:

```powershell
python -m src.helper.cli trello-inspect
```

Or manually:
1. Open a job card in your list
2. Look at the URL: `https://trello.com/c/xyz123abc/...`
3. Click on "Show details" or open browser DevTools (F12)
4. Copy the list ID from the card's list

### 6.6 Create a Template Card (Optional but Recommended)

The application can copy checklists from a template card. This is optional but saves time if you have standard steps for all job applications.

**Steps:**
1. Create a new card in your "Leads" list named "🔖 Template" (or similar)
2. Add a checklist with your standard steps, e.g.:
   - [ ] Cover letter generated
   - [ ] Application submitted
   - [ ] Follow-up reminder set
   - [ ] Feedback received
3. Get the card ID from the URL or use diagnostic CLI
4. (Optional) Add this to `config/.env` as `TRELLO_TEMPLATE_CARD_ID`

### 6.7 Add Credentials to Environment

Update `config/.env`:
```bash
TRELLO_KEY=your-api-key
TRELLO_TOKEN=your-token
TRELLO_BOARD_ID=your-board-id
TRELLO_LIST_ID_LEADS=your-list-id
```

## Step 7: Optional - Set Up Labels (Color-Coding)

Labels help organize your job applications by work mode, language, and seniority level.

### 7.1 Create Labels in Trello

1. Open your board
2. Click "Labels" (or right-click on a card → Labels)
3. Create the following labels:

**Work Mode:**
- Remote (Blue)
- Hybrid (Green)
- Onsite (Orange)

**Language:**
- German (Red)
- English (Blue)

**Seniority:**
- Junior (Light Blue)
- Mid (Yellow)
- Senior (Purple)
- Lead (Red)

### 7.2 Get Label IDs

Use the diagnostic CLI:

```powershell
python -m src.helper.cli trello-inspect
```

This will show all labels and their IDs.

### 7.3 Add to Environment

Update `config/.env` with label IDs (optional):
```bash
# Work Mode
TRELLO_LABEL_REMOTE=label-id-here
TRELLO_LABEL_HYBRID=label-id-here
TRELLO_LABEL_ONSITE=label-id-here

# Language
TRELLO_LABEL_DE=label-id-here
TRELLO_LABEL_EN=label-id-here

# Seniority
TRELLO_LABEL_JUNIOR=label-id-here
TRELLO_LABEL_MID=label-id-here
TRELLO_LABEL_SENIOR=label-id-here
TRELLO_LABEL_LEAD=label-id-here
```

The application will automatically apply these labels based on detected job attributes.

## Step 8: Optional - Set Up Custom Fields

Custom fields let you structure data (company name, job title, source, etc.) in Trello.

### 8.1 Create Custom Fields in Trello

1. Open your board
2. Click "Power-Ups" (top-right) → "Custom Fields"
3. Create the following fields:

| Field Name | Type | Notes |
|-----------|------|-------|
| Company Name | Text | |
| Job Title | Text | |
| Source | Dropdown | Options: Stepstone, LinkedIn |
| Publication Date | Date | |
| Contact Person | Text | Optional |

### 8.2 Get Custom Field IDs

Use the diagnostic CLI:

```powershell
python -m src.helper.cli trello-inspect
```

### 8.3 Add to Environment

Update `config/.env`:
```bash
TRELLO_FIELD_COMPANY_NAME=field-id-here
TRELLO_FIELD_JOB_TITLE=field-id-here
TRELLO_FIELD_SOURCE=field-id-here
TRELLO_FIELD_PUBLICATION_DATE=field-id-here
```

## Step 9: Optional - Set Up Word Templates

The application can export cover letters to `.docx` using professional templates. This is optional—if templates are missing, basic `.docx` files are generated.

### 9.1 Create Word Templates

1. Open Microsoft Word (or compatible software)
2. Create a professional cover letter template with these **placeholders**:

```
{{SENDER_NAME}}
{{SENDER_ADDRESS_LINE1}}
{{SENDER_ADDRESS_LINE2}}
{{SENDER_PHONE}}
{{SENDER_EMAIL}}
{{SENDER_LINKEDIN}}
{{SENDER_PORTFOLIO}}

{{DATE}}

{{COMPANY_NAME}}
{{COMPANY_ADDRESS_LINE1}}
{{COMPANY_ADDRESS_LINE2}}

{{COVER_LETTER_SALUTATION}}

{{COVER_LETTER_BODY}}

{{COVER_LETTER_VALEDICTION}}
```

> **Pro tip:** Use table layouts to control spacing and formatting. Placeholders are replaced with your actual values.

### 9.2 Save Templates

- **German:** Save as `data/template_de.docx`
- **English:** Save as `data/template_en.docx`

## Step 10: Verify Setup

Run the diagnostic check:

```powershell
python -m src.helper.cli trello-auth
```

This verifies your Trello credentials are working.

## Step 11: Test Everything

### Test 1: Scrape a Job Posting

Find a job URL from Stepstone or LinkedIn and test:

```powershell
python src/main.py https://www.stepstone.de/jobs/...
```

Expected output:
- ✅ Job data extracted
- ✅ Trello card created
- ✅ Cover letter generated
- ✅ `.docx` saved to `output/cover_letters/`

### Test 2: Web UI (Optional)

```powershell
python src/app.py
# Open http://localhost:5000
```

## Configuration Reference

Your complete `config/.env` file should look like:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key

# Trello (Required)
TRELLO_KEY=your-api-key
TRELLO_TOKEN=your-token
TRELLO_BOARD_ID=your-board-id
TRELLO_LIST_ID_LEADS=your-list-id

# Trello Labels (Optional)
TRELLO_LABEL_REMOTE=label-id
TRELLO_LABEL_HYBRID=label-id
TRELLO_LABEL_ONSITE=label-id
TRELLO_LABEL_DE=label-id
TRELLO_LABEL_EN=label-id
TRELLO_LABEL_JUNIOR=label-id
TRELLO_LABEL_MID=label-id
TRELLO_LABEL_SENIOR=label-id
TRELLO_LABEL_LEAD=label-id

# Trello Custom Fields (Optional)
TRELLO_FIELD_COMPANY_NAME=field-id
TRELLO_FIELD_JOB_TITLE=field-id
TRELLO_FIELD_SOURCE=field-id
TRELLO_FIELD_PUBLICATION_DATE=field-id

# Trello Template Card (Optional)
TRELLO_TEMPLATE_CARD_ID=card-id
```

## Next Steps

1. **Scrape job postings** from Stepstone or LinkedIn
2. **Review generated cover letters** in `output/cover_letters/`
3. **Customize templates** in `data/template_de.docx` and `data/template_en.docx` as needed
4. **Start automating your applications!** 🚀

## Support

- **Issues?** Check existing issues on GitHub
- **Questions?** See the README.md for more information
- **Help with Trello?** Use `python -m src.helper.cli trello-inspect` to debug

