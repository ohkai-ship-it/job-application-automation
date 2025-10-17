# Placeholder Cover Letter Feature - Summary

## What Was Done

Added a testing mode to bypass OpenAI API calls and use a placeholder cover letter instead.

## Changes Made

### 1. Modified `src/main.py`
- Added environment variable check: `USE_PLACEHOLDER_COVER_LETTER`
- When set to `true`, generates a 200-word placeholder instead of calling OpenAI
- Placeholder text is customized with actual company name and job title
- All other workflow steps (DOCX, PDF generation) work normally

### 2. Created Test Scripts
- `test_app_with_placeholder.ps1` - PowerShell script to run Flask with placeholder mode
- `test_app_with_placeholder.bat` - Batch file for Windows Command Prompt
- `docs/TESTING_WITHOUT_OPENAI.md` - Complete documentation

## How to Use

**Quick Start:**
```powershell
.\test_app_with_placeholder.ps1
```

**Manual:**
```powershell
$env:USE_PLACEHOLDER_COVER_LETTER = "true"
python src/app.py
```

## Placeholder Details

- **Word Count:** 203 words (target was 200)
- **Language:** English (default)
- **Customization:** Uses actual company name and job title from scraped data
- **Structure:** Professional cover letter format
- **Output:** Saved to TXT, DOCX, and PDF formats

## Example Placeholder Text

```
I am writing to express my strong interest in the [JOB_TITLE] position at [COMPANY].
With my extensive background in software development and proven track record of delivering
high-quality solutions, I am confident that I would be a valuable addition to your team.
[... continues for ~200 words total ...]
```

## Use Cases

✅ **When OpenAI rate limits are reached** (like now - 10+ hours wait)
✅ **During development and testing** to save API credits
✅ **Testing workflow without AI dependency**
✅ **Fast iteration on other features**

## Testing Status

- ✅ All 124 unit tests passing
- ✅ Placeholder generation tested and verified
- ✅ Word count confirmed: 203 words
- ✅ Integration with existing workflow confirmed
- ✅ No breaking changes to existing functionality

## Reverting to AI Mode

Simply run without the environment variable or set it to `false`:

```powershell
python src/app.py
```

## Implementation Notes

The implementation:
1. Checks `os.getenv('USE_PLACEHOLDER_COVER_LETTER')` in `src/main.py`
2. If true, skips `CoverLetterGenerator` initialization
3. Builds placeholder text with company/position interpolation
4. Continues with normal DOCX/PDF generation workflow
5. Logs clearly when placeholder mode is active

This is a **non-breaking change** - existing functionality works exactly as before when the environment variable is not set.
