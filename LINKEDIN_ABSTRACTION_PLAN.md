# LinkedIn URL Normalization & Abstraction Plan

## Problem Analysis

### The Two URLs
1. **Recommended/Collection URL** (works):
   ```
   https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4308732682
   ```

2. **Direct Job View URL** (doesn't work):
   ```
   https://www.linkedin.com/jobs/view/4308732682/?alternateChannel=search&eBP=...&refId=...&trackingId=...
   ```

Both point to the **same job posting (4308732682)** but have different:
- Path structure (`/collections/recommended/` vs `/jobs/view/`)
- Query parameters (minimal vs heavy tracking params)
- Navigation context (collection view vs direct view)

**Current Issue:** Our scraper may handle one format but not the other due to:
- Playwright navigation differences
- Different DOM structure after rendering
- Timing/loading differences

---

## Root Cause Analysis

### Why Direct URL Might Fail

1. **Different page structure** - Direct job view may render differently than collection view
2. **Different selector paths** - DOM structure likely varies
3. **Different loading behavior** - May have different network requirements
4. **Tracking parameters** - LinkedIn may serve different content based on UTM/tracking params

### Current Code Weakness

```python
# Current approach in scrape_linkedin_job():
direct_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

# Only tries ONE format, doesn't handle variations
await page.goto(direct_url, ...)
```

**Problem:** Hardcoded to one URL format. If that format fails, no fallback.

---

## Solution Plan (3 Phases)

### PHASE 1: URL Normalization
**Goal:** Extract job ID and normalize to canonical format

**Implementation:**
```python
def normalize_linkedin_url(url: str) -> Tuple[str, str]:
    """
    Normalize any LinkedIn job URL to canonical format.
    
    Args:
        url: Any LinkedIn job URL variant
        
    Returns:
        Tuple of (job_id, canonical_url)
        
    Handles:
    - /collections/recommended/?currentJobId=XXX
    - /jobs/view/XXX/
    - /jobs/view/XXX/?param=value...
    - Future variations
    """
    # Extract job ID (already have this)
    job_id = extract_job_id_from_url(url)
    
    # Return canonical format
    canonical = f"https://www.linkedin.com/jobs/view/{job_id}/"
    
    return job_id, canonical
```

**Files to modify:**
- `src/linkedin_scraper.py` - Add `normalize_linkedin_url()`
- Update `scrape_linkedin_job()` to use it

---

### PHASE 2: Multi-Format Scraping Strategy
**Goal:** Try multiple rendering approaches if primary fails

**Implementation:**
```python
async def extract_job_description_with_fallbacks(job_id: str) -> Optional[str]:
    """
    Try multiple URLs and rendering strategies.
    
    Tries in order:
    1. Direct job view URL
    2. Collection URL (original format)
    3. Search result URL (if we have it)
    """
    urls_to_try = [
        f"https://www.linkedin.com/jobs/view/{job_id}/",
        f"https://www.linkedin.com/jobs/collections/recommended/?currentJobId={job_id}",
    ]
    
    for attempt_url in urls_to_try:
        try:
            description = await extract_job_description_playwright(attempt_url)
            if description and len(description) > 500:
                return description
        except Exception as e:
            print(f"Attempt {attempt_url} failed: {e}, trying next...")
            continue
    
    return None
```

**Benefits:**
- Resilient to URL format changes
- Tries most likely to work first
- Falls back to other formats
- Graceful degradation

**Files to modify:**
- `src/linkedin_scraper.py` - Add `extract_job_description_with_fallbacks()`

---

### PHASE 3: Improve DOM Selection Robustness
**Goal:** Handle different DOM structures across URL variants

**Implementation:**
```python
async def extract_job_description_from_rendered_page(page, job_id: str) -> Optional[str]:
    """
    Extract description from already-loaded Playwright page.
    
    Tries multiple selectors and strategies:
    1. Standard description selectors
    2. Alternative selectors for different page variants
    3. Content aggregation as last resort
    """
    selectors = [
        # Try most specific first
        '[data-test-id="job-description"]',
        'div.show-more-less-html__markup',
        
        # Try alternative structures
        '.jobs-details__main-content',
        '.jobs-details-top-card',
        'section.description',
        
        # Fallback: look for any substantial text block
        'article',
        'main',
    ]
    
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if await element.is_visible():
                text = await element.text_content()
                if text and len(text.strip()) > 500:
                    return text
        except:
            continue
    
    # Last resort: aggregate all substantial text
    return await aggregate_page_text(page)
```

**Benefits:**
- Handles DOM variation across URLs
- Multiple fallback strategies
- More robust selector matching
- Aggregation as safety net

---

## Implementation Roadmap

### Step 1: Add URL Normalization (5 min)
```python
# In linkedin_scraper.py, add function
def normalize_linkedin_url(url: str) -> Tuple[str, str]
```
- Extract job ID
- Return canonical URL
- Simple, low-risk

### Step 2: Test Both URL Formats (2 min)
```bash
python -c "from src.linkedin_scraper import scrape_linkedin_job; print(scrape_linkedin_job('URL1')); print(scrape_linkedin_job('URL2'))"
```
- Verify which one fails
- Get error message
- Understand why

### Step 3: Add Fallback URLs (10 min)
```python
# In scrape_linkedin_job(), replace:
direct_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

# With:
urls_to_try = [
    f"https://www.linkedin.com/jobs/view/{job_id}/",
    f"https://www.linkedin.com/jobs/collections/recommended/?currentJobId={job_id}",
]
job_description = await extract_with_fallbacks(urls_to_try)
```

### Step 4: Improve Selectors (10 min)
- Test both URLs in Playwright
- Inspect DOM structure differences
- Add selectors as needed

### Step 5: Test Both URLs (5 min)
```bash
python test_both_urls.py
```

### Step 6: Run Full Test Suite (2 min)
```bash
pytest tests/ -v
```

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Break existing URL | Low | Test both during development |
| Selector conflicts | Low | Test each selector independently |
| Performance impact | Low | Fallback only on failure |
| Browser issues | Very low | Already using Playwright error handling |

---

## Estimated Effort
- **Phase 1 (URL Normalization)**: 15 minutes
- **Phase 2 (Multi-Format)**: 20 minutes
- **Phase 3 (DOM Robustness)**: 25 minutes
- **Testing & Verification**: 10 minutes

**Total: ~70 minutes**

---

## Success Criteria

✅ Both URLs work and return same job_data  
✅ All 148 existing tests still pass  
✅ No performance degradation  
✅ Graceful fallback on failure  
✅ Code documented and maintainable  

---

## Files to Create/Modify

**Modify:**
- `src/linkedin_scraper.py` - Add normalization + fallback logic

**Create (Optional):**
- `test_both_urls.py` - Verify both URL formats work

**No Breaking Changes** to:
- Public API
- Job data format
- Trello integration
- Existing tests

---

## Next Steps

Should I:
1. **Go ahead with implementation** (do all 3 phases)
2. **Test first** (verify which URL fails and why)
3. **Minimal fix only** (just add fallback URLs)

My recommendation: **Test first** (2 min) → then implement based on findings.

Want me to proceed with testing to see exactly where the second URL fails?
