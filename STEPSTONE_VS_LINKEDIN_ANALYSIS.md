# Stepstone vs LinkedIn: Trello Card Integration Analysis

**Date**: October 23, 2025  
**Status**: ✅ Investigation Complete, LinkedIn Source Support Added

## Executive Summary

Both Stepstone and LinkedIn job postings can be scraped and added to Trello, but there are key differences in how links are attached and sources are tracked. This document outlines these differences and the fix implemented.

---

## Architecture Overview

### Job Scraping Flow

```
User URL
   ↓
detect_job_source(url) → 'stepstone' | 'linkedin'
   ↓
StepstoneScraper.scrape() OR LinkedInScraper.scrape()
   ↓
job_data dict with:
   - company_name
   - job_title
   - job_description
   - source_url
   - website_link
   - career_page_link
   - [other fields]
   ↓
TrelloConnect.create_card_from_job_data()
   ↓
Trello Card Created
```

### Trello Card Components

1. **Card Name**: `[Company] Title (Location)`
2. **Card Description**: Complete job description
3. **Card Attachments**: Links to job posting and optional career page
4. **Custom Fields**: 
   - Quelle (Source): Stepstone / LinkedIn / Unknown
   - Sprache (Language): DE / EN
   - Seniority: Junior / Mid / Senior / Lead
   - Work Mode: Remote / Hybrid / Onsite
5. **Labels**: Based on language, seniority, work mode

---

## Key Differences: Stepstone vs LinkedIn

### 1. Link Attachment (Card Attachments)

#### Stepstone
```python
# StepstoneScraper extracts:
job_data = {
    'source_url': 'https://www.stepstone.de/stellenangebote--...',
    'website_link': 'https://company.com',
    'career_page_link': 'https://company.com/careers',  # May be present
    'direct_apply_link': 'https://...'  # Extracted link
}
```

**Trello Attachment Process** (in `_add_attachments`):
```
Attachment 1: "Ausschreibung" (Job Posting)
   → source_url (the Stepstone link)

Attachment 2: "Firmenportal" (Career Page)
   → career_page_link (if available, from scraper)
```

#### LinkedIn
```python
# LinkedInScraper extracts:
job_data = {
    'source_url': 'https://www.linkedin.com/jobs/view/4253399100',
    'website_link': '',  # Usually empty
    'career_page_link': '',  # Usually empty
    'direct_apply_link': ''  # Not extracted from static HTML
}
```

**Trello Attachment Process** (in `_add_attachments`):
```
Attachment 1: "Ausschreibung" (Job Posting)
   → source_url (the LinkedIn link)

Attachment 2: "Firmenportal" (Career Page)
   → career_page_link (usually empty/missing)
```

**Key Difference**: LinkedIn doesn't provide career page or company website links (they're not in the static HTML). Only the job posting URL is attached.

---

### 2. Source Field Setting (Quelle Custom Field)

#### Previous Implementation (BUG ⚠️)

```python
# trello_connect.py _set_custom_fields() method (line 310-330)

# List/dropdown field: Quelle (Source) - set to "Stepstone" for Stepstone URLs
if self.field_source_list and self.field_source_stepstone_option:
    source_url = job_data.get('source_url', '')
    if 'stepstone' in source_url.lower():
        # Set Quelle field to Stepstone option
        ...
    # ❌ PROBLEM: LinkedIn URLs are NOT handled!
    # Result: LinkedIn cards have Quelle field left blank/empty
```

#### Fixed Implementation ✅

```python
# NEW: Both Stepstone and LinkedIn sources are now supported

if self.field_source_list:
    source_url = job_data.get('source_url', '')
    source_option_id = None
    source_name = 'Unknown'
    
    if 'stepstone' in source_url.lower() and self.field_source_stepstone_option:
        source_option_id = self.field_source_stepstone_option
        source_name = 'Stepstone'
    elif 'linkedin' in source_url.lower() and self.field_source_linkedin_option:
        source_option_id = self.field_source_linkedin_option
        source_name = 'LinkedIn'
    
    if source_option_id:
        # Set Quelle field to appropriate option
        ...
```

**Key Changes**:
- ✅ Added `TRELLO_FIELD_QUELLE_LINKEDIN` environment variable support
- ✅ Checks for both Stepstone AND LinkedIn URLs
- ✅ Sets source field appropriately for each platform
- ✅ Logs source name for debugging

---

## Configuration Required

### Environment Variables for LinkedIn Source Support

Add to `config/.env`:

```bash
# Trello Custom Field: Quelle (Source)
TRELLO_FIELD_QUELLE=<field-id>

# Quelle Options
TRELLO_FIELD_QUELLE_STEPSTONE=<option-id>        # Already existed
TRELLO_FIELD_QUELLE_LINKEDIN=<option-id>          # NEW - add this
```

### How to Get Option IDs

Run the diagnostic command:
```bash
python -m src.helper.cli trello-inspect
```

This shows all custom fields and their options for your Trello board.

---

## Data Flow Comparison

### Stepstone Flow

```
Stepstone URL
    ↓
StepstoneScraper.scrape()
    ├─ Extracts via JSON-LD
    ├─ source_url = Stepstone link
    ├─ website_link = Company website
    └─ career_page_link = Company careers page
    ↓
TrelloConnect.create_card_from_job_data()
    ├─ Attachments:
    │  ├─ "Ausschreibung" → Stepstone link ✓
    │  └─ "Firmenportal" → Career page ✓
    └─ Custom Field Quelle:
       └─ Set to "Stepstone" option ✓
```

### LinkedIn Flow

```
LinkedIn URL
    ↓
LinkedInScraper.scrape()
    ├─ Extracts via static HTML parsing
    ├─ source_url = LinkedIn link
    ├─ website_link = (empty)
    └─ career_page_link = (empty)
    ↓
TrelloConnect.create_card_from_job_data()
    ├─ Attachments:
    │  ├─ "Ausschreibung" → LinkedIn link ✓
    │  └─ "Firmenportal" → (empty, not added)
    └─ Custom Field Quelle:
       └─ Set to "LinkedIn" option ✓ (NEW)
```

---

## Implementation Changes Made

### 1. Removed Backward Compatibility Layer ✅

**Files Modified**: 
- `src/scraper.py`
- `src/linkedin_scraper.py`
- `src/main.py`

**Removed Functions** (no longer needed):
```python
# scraper.py
- clean_job_title()           # Use StepstoneScraper._clean_job_title()
- split_address()              # Use StepstoneScraper._split_address()
- extract_company_address_from_description()  # Use StepstoneScraper._extract_address_from_description()
- scrape_stepstone_job_async() # Use StepstoneScraper().scrape()
- scrape_stepstone_job()       # Use StepstoneScraper().scrape() (async)

# linkedin_scraper.py
- extract_job_id_from_url()    # Use LinkedInScraper()._extract_job_id()
- scrape_linkedin_job_async()  # Use LinkedInScraper().scrape()
- scrape_linkedin_job()        # Use LinkedInScraper().scrape() (async)
```

**Why Removed**:
- Scrapers are now fully class-based
- All internal usage updated to use classes directly
- Eliminates maintenance overhead
- Cleaner API surface

### 2. Enhanced LinkedIn Source Support in Trello ✅

**File Modified**: `src/trello_connect.py`

**Changes**:
- Added `self.field_source_linkedin_option` configuration
- Updated `_set_custom_fields()` to handle LinkedIn sources
- Both Stepstone and LinkedIn now properly set the Quelle field

---

## Testing Checklist

### Before Merging

- [ ] Run existing tests with removed backward compat functions
- [ ] Test Stepstone URL → Trello card creation
  - [ ] Verify "Ausschreibung" attachment points to Stepstone
  - [ ] Verify "Firmenportal" attachment exists if career page available
  - [ ] Verify Quelle field set to "Stepstone"
  - [ ] Verify other custom fields set correctly
- [ ] Test LinkedIn URL → Trello card creation
  - [ ] Verify "Ausschreibung" attachment points to LinkedIn
  - [ ] Verify Quelle field set to "LinkedIn" (requires env var)
  - [ ] Verify other custom fields set correctly
- [ ] Check logs for source detection messages

### Example Test Commands

```python
# Test Stepstone scraping (class-based)
from src.scraper import StepstoneScraper
import asyncio

async def test():
    scraper = StepstoneScraper()
    url = "https://www.stepstone.de/stellenangebote--..."
    data = await scraper.scrape(url)
    print(data['source_url'])  # Should be Stepstone URL

asyncio.run(test())

# Test LinkedIn scraping (class-based)
from src.linkedin_scraper import LinkedInScraper

async def test():
    scraper = LinkedInScraper()
    url = "https://www.linkedin.com/jobs/view/..."
    data = await scraper.scrape(url)
    print(data['source_url'])  # Should be LinkedIn URL

asyncio.run(test())
```

---

## Documentation Updates Needed

### Update Files
1. `docs/API.md` - Document class-based scraper APIs
2. `docs/DEVELOPMENT.md` - Update scraper usage examples
3. `README.md` - Update scraper instructions
4. `.env.example` - Add `TRELLO_FIELD_QUELLE_LINKEDIN`

---

## Future Enhancements

### Potential Improvements

1. **Add more job sources**: 
   - Indeed.com
   - Glassdoor
   - Custom job board integration
   - Just add new Scraper subclass + option ID

2. **Enhanced LinkedIn extraction**:
   - Use Playwright for better job detail extraction
   - Extract company website from LinkedIn company page
   - Extract job posting date/seniority level

3. **Source-specific Trello labels**:
   - Auto-apply platform-specific label (e.g., "LinkedIn", "Stepstone")
   - Different processing rules per source

---

## Summary of Changes

| Aspect | Before | After | Impact |
|--------|--------|-------|--------|
| **Backward Compat** | 8 functions | Removed | ✅ Cleaner API |
| **Stepstone Source** | Set in Quelle | Set in Quelle | ✅ Works |
| **LinkedIn Source** | NOT set | Set in Quelle | ✅ Fixed |
| **Code Complexity** | Higher | Lower | ✅ Maintainable |
| **Configuration** | 1 env var | 2 env vars | ⚠️ Requires setup |

---

## Commit Message

```
refactor: Remove backward compat functions and add LinkedIn Trello support

Breaking Changes:
- Removed deprecated scraper wrapper functions (scrape_stepstone_job, etc.)
- Updated main.py to use class-based scrapers directly
- Requires code update for any external usage

Features:
- Add LinkedIn source support to Trello Quelle field
- Add TRELLO_FIELD_QUELLE_LINKEDIN configuration
- Both Stepstone and LinkedIn now properly tracked in Trello

Improvements:
- Cleaner, class-based API surface
- Less maintenance burden
- Better source tracking for both platforms
- Improved logging for source detection
```

---

**Investigation Complete** ✅  
All changes ready for testing and merge.
