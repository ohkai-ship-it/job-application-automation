# Production Setup Guide

This guide will help you set up the Job Application Automation tool for production use.

## Prerequisites

- **Python**: 3.10 or higher
- **Git**: For version control
- **Internet connection**: For API access and web scraping
- **Operating System**: Windows, macOS, or Linux

## Quick Start (5 minutes)

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd job-application-automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Credentials

Create a `config/.env` file with your API keys:

```
OPENAI_API_KEY=sk-your-key-here
TRELLO_KEY=your-trello-key
TRELLO_TOKEN=your-trello-token
TRELLO_BOARD_ID=your-board-id
TRELLO_LIST_ID_LEADS=your-list-id
```

### 3. Start the Web Interface

```bash
python src/app.py
```

Then open your browser to: **http://localhost:5000**

---

## Detailed Credential Setup

### Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to **API keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)
6. Add to `config/.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

**Cost**: ~$0.01 per cover letter generated

### Getting Trello Credentials

#### 1. Get Trello API Key

1. Go to [Trello Developer](https://trello.com/app-key)
2. Log in with your Trello account
3. Copy your **API Key**
4. Add to `config/.env`:
   ```
   TRELLO_KEY=your-api-key
   ```

#### 2. Generate Trello Token

1. On the same [Trello Developer](https://trello.com/app-key) page
2. Scroll down and click **Generate a Token**
3. Click **Generate** on the popup
4. Copy the token
5. Add to `config/.env`:
   ```
   TRELLO_TOKEN=your-token
   ```

#### 3. Find Your Board ID

1. Go to your Trello board in the browser
2. The URL will look like: `https://trello.com/b/BOARD_ID/board-name`
3. Copy the `BOARD_ID` (the 8 characters after `/b/`)
4. Add to `config/.env`:
   ```
   TRELLO_BOARD_ID=your-board-id
   ```

#### 4. Find Your List ID

1. In your Trello board, find the list where you want cards created (e.g., "Leads")
2. Open your browser's Developer Tools (F12)
3. Go to the **Console** tab
4. Run this command:
   ```javascript
   fetch('/1/boards/YOUR_BOARD_ID/lists').then(r => r.json()).then(lists => console.table(lists.map(l => ({name: l.name, id: l.id}))))
   ```
   (Replace `YOUR_BOARD_ID` with your actual board ID)
5. Find your list in the output and copy its ID
6. Add to `config/.env`:
   ```
   TRELLO_LIST_ID_LEADS=your-list-id
   ```

---

## Running the Application

### Web Interface (Recommended for Most Users)

```bash
python src/app.py
```

Features:
- **Batch Processing**: Process multiple job URLs at once
- **Progress Tracking**: Real-time progress updates
- **Downloadable Files**: Access generated cover letters
- **Simple UI**: No technical knowledge required

Visit: **http://localhost:5000**

### Command Line Interface

Process a single URL:

```bash
python src/main.py https://www.stepstone.de/jobs/...
```

Process multiple URLs:

```bash
python src/main.py url1 url2 url3
```

---

## Features & What Gets Generated

### 1. Trello Card Creation

A card is created with:
- Job title and company name
- Job description and requirements
- Link to the job posting
- Custom fields for tracking
- Checklist for application steps

### 2. Cover Letter Generation

AI-generated cover letters that:
- Match the job requirements
- Reference your CV
- Are 180-240 words long
- Automatically detect job language (German or English)
- Include proper salutations and sign-offs

### 3. Document Formats

- **DOCX** (Microsoft Word): Easy to edit
- **PDF**: Professional format for submission
- **TXT**: Plain text backup

---

## Production Configuration

### Logging

Logs are automatically saved to `logs/app.log` with:
- Rotating file handler (prevents disk space issues)
- JSON format for easy parsing
- Both file and console output

View logs:

```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View JSON logs
cat logs/app.log | grep '{"timestamp'
```

### Health Checks

Monitor application health:

```bash
curl http://localhost:5000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:45.123456",
  "services": {
    "database": "ok",
    "trello": "ok",
    "openai": "ok"
  }
}
```

### Error Resilience

The application includes automatic retry logic:

- **Rate Limit Errors**: Retry with exponential backoff (1s, 2s, 4s delays)
- **Temporary API Failures**: Automatically retry up to 3 times
- **Optional Services**: Continue without Trello or PDF if they fail

---

## Troubleshooting

### Problem: "MISSING REQUIRED CREDENTIALS"

**Solution**: Make sure `config/.env` file exists and contains all required keys.

Check file location:
```bash
# Should be in the project root
ls -la config/.env
```

### Problem: "OpenAI API Error: Invalid API key"

**Solution**: 
1. Verify the API key starts with `sk-`
2. Check it's not expired on [OpenAI Platform](https://platform.openai.com/account/api-keys)
3. Generate a new key if needed

### Problem: "Trello: Authentication failed"

**Solution**:
1. Verify both `TRELLO_KEY` and `TRELLO_TOKEN` are correct
2. Check they haven't expired
3. Generate new credentials from [Trello Developer](https://trello.com/app-key)

### Problem: "PDF conversion failed"

**Solution**: This is non-critical. The DOCX file is still created.

To enable PDF conversion:
```bash
pip install docx2pdf
```

### Problem: "No database found"

**Solution**: The database is created automatically on first run. Check file permissions:

```bash
# Ensure output directory exists and is writable
chmod 755 output/
```

### Problem: Application won't start

**Solution**: Check for missing dependencies:

```bash
# Verify all packages are installed
pip list | grep -E "flask|openai|python-docx"

# Reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

---

## Performance Tips

### 1. Batch Processing

Process multiple jobs at once:
- Load 10+ URLs at once using the web interface
- Application processes them sequentially
- Much more efficient than manual processing

### 2. Disable Optional Features

If you only need Trello cards:
```bash
# Uncheck "Generate Documents" in the UI
```

If you only need cover letters:
```bash
# Uncheck "Create Trello Card" in the UI
```

### 3. Skip Duplicate Checking

For re-processing a job:
- The application automatically detects duplicates
- Duplicates are skipped by default (in production mode)
- To reprocess, enable the skip in the UI

---

## Maintenance

### Updating Dependencies

Check for package updates:

```bash
pip list --outdated
pip install -r requirements.txt --upgrade
```

### Clearing Logs

Logs rotate automatically (10MB per file, 5 backups kept).

To manually clear:

```bash
rm -f logs/app.log*
```

### Backing Up Credentials

**⚠️  NEVER commit `config/.env` to version control!**

To safely backup credentials:

```bash
# Backup (keep in a safe location)
cp config/.env config/.env.backup

# Restore
cp config/.env.backup config/.env
```

---

## Security Best Practices

✅ **DO:**
- Keep API keys in `config/.env` (already in `.gitignore`)
- Use strong Trello tokens
- Regularly rotate credentials
- Monitor logs for suspicious activity
- Run on a secure network

❌ **DON'T:**
- Share API keys
- Commit `.env` to version control
- Log sensitive data
- Use weak API keys
- Run on public networks without authentication

---

## Getting Help

### Check the Logs

Most issues are logged with details:

```bash
tail -50 logs/app.log
```

### Run Tests

Verify everything is working:

```bash
python -m pytest -v
```

### Check Health Endpoint

```bash
curl http://localhost:5000/health | python -m json.tool
```

### Common Issues Forum

See [GitHub Issues](https://github.com/your-repo/issues) for common solutions.

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up API keys
3. ✅ Start the application
4. ✅ Process your first job posting
5. ✅ Check the generated files
6. ✅ Review and download cover letters

**Happy applying!** 🚀
