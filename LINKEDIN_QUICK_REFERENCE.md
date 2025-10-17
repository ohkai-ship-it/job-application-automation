# LinkedIn Integration - Quick Reference After Restart

## 🚀 Getting Started Again

After VS Code restart, here's the quickest way to continue:

### 1. **Test the Integration**
```bash
python debug_linkedin_integration.py
```
This will systematically test:
- URL detection (LinkedIn vs Stepstone)
- Trello configuration loading
- Trello connection
- LinkedIn scraper with the new URL

### 2. **Run Specific Tests**
```bash
# Test just the LinkedIn scraper
python -m pytest tests/unit/test_linkedin_scraper.py -v

# Test main integration
python -m pytest tests/unit/test_linkedin_scraper.py::TestMainIntegration -v
```

### 3. **Manual Testing**
```bash
# Test URL detection
python -c "from src.main import detect_job_source; print(detect_job_source('https://www.linkedin.com/jobs/view/4294449394/'))"

# Test scraper directly
python test_linkedin_url.py
```

## 📊 Current State

### Working ✓
- URL detection (LinkedIn/Stepstone)
- Job ID extraction from LinkedIn URLs
- Basic job data scraping
- Test suite (19 tests passing)
- Trello configuration loaded
- LinkedIn source option found in Trello

### Needs Debugging ✗
1. **Job description text incomplete** - May need timeout handling or fallback
2. **Quelle field not set to LinkedIn** - Need to verify API call
3. **Career portal link not attached** - Need to check attachment logic

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/linkedin_scraper.py` | LinkedIn job scraper |
| `src/main.py` | URL detection & routing |
| `src/trello_connect.py` | Trello API integration |
| `config/.env` | Config (includes LinkedIn field ID) |
| `debug_linkedin_integration.py` | Debugging script |
| `CHECKPOINT_LINKEDIN_INTEGRATION.md` | Detailed checkpoint |

## 🔗 Test URLs

**New URL to test:**
```
https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4294449394
```

## 💡 Debugging Order

1. Check if scraper can fetch LinkedIn page (may timeout)
2. Verify job_data is complete
3. Check if Trello config values are loaded
4. Test Trello field updates individually
5. Check Trello API responses

## ⚠️ Known Issues

- **LinkedIn blocking**: Direct scraping may fail if LinkedIn blocks requests
- **Timeout**: Need to handle timeouts gracefully (5 second timeout set)
- **Authentication**: LinkedIn may require login for full description

## 🎯 Success Criteria

After debugging, you should be able to:
1. ✓ Paste a LinkedIn URL
2. ✓ Auto-detect it's LinkedIn
3. ✓ Scrape job data successfully
4. ✓ Create Trello card with:
   - Quelle set to "LinkedIn"
   - "Ausschreibung" attachment (LinkedIn URL)
   - "Firmenportal" attachment (company career page)
   - Full job description

## 📝 Notes

- All code changes are on `feature/linkedin-integration` branch
- No breaking changes to Stepstone workflow
- Tests thoroughly cover LinkedIn scraper
- Ready for production after debugging Trello issues

---

**Last Updated**: October 16, 2025 - Before VS Code Restart
