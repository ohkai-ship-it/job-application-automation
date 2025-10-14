# Testing Without OpenAI

When you need to test the application without making OpenAI API calls (e.g., during rate limits or for development), you can use the placeholder mode.

## How to Enable Placeholder Mode

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\test_app_with_placeholder.ps1
```

### Option 2: Using Batch File
```cmd
test_app_with_placeholder.bat
```

### Option 3: Manual Environment Variable
Set the environment variable before running the app:

**PowerShell:**
```powershell
$env:USE_PLACEHOLDER_COVER_LETTER = "true"
python src/app.py
```

**Command Prompt:**
```cmd
set USE_PLACEHOLDER_COVER_LETTER=true
python src/app.py
```

## What Happens in Placeholder Mode

- ✅ OpenAI API calls are completely bypassed
- ✅ A 200-word placeholder cover letter is generated instead
- ✅ All other functionality works normally (scraping, Trello, DOCX, PDF)
- ✅ The placeholder text is customized with the actual company name and job title
- ✅ Default language is set to English

## Placeholder Text Details

The generated placeholder:
- Contains approximately 200 words (203 words exactly)
- Uses professional language suitable for job applications
- Includes company name and position from scraped data
- Follows standard cover letter structure
- Is saved to all formats (TXT, DOCX, PDF) just like AI-generated letters

## When to Use This

- 🚫 OpenAI rate limits reached
- 🧪 Testing the application workflow
- 🔧 Developing new features without AI dependency
- 💰 Conserving OpenAI API credits during development
- ⚡ Fast testing iterations

## Switching Back to AI Mode

Simply run the app normally without setting the environment variable, or set it to `false`:

```powershell
$env:USE_PLACEHOLDER_COVER_LETTER = "false"
python src/app.py
```

Or just run without any environment variable:
```powershell
python src/app.py
```
