# Scraper Architecture: Design & Future Plans

## Current State: v0.1 - LinkedIn Collection Scraper

### Implemented ✅
- **Stepstone Scraper**: Stable, production-ready
- **LinkedIn Collection Scraper**: New in v0.1, handles `collections/recommended/?currentJobId=XXX` format
  - Full job description extraction via Playwright (JavaScript rendering)
  - Company name, title, location, address extraction
  - Career portal link generation
  - Quelle field integration with Trello

### Features
- Auto-detection of platform (LinkedIn vs Stepstone) via URL matching
- Unified `job_data` format across platforms
- Graceful fallback to static HTML parsing if Playwright unavailable
- Comprehensive test coverage (19 LinkedIn-specific tests)

### Known Limitations
- LinkedIn direct view URLs (`/jobs/view/`) not yet supported
- No career portal enrichment (address often incomplete)
- No publication date extraction
- No contact person extraction
- Company address extraction from description only (lower confidence)

---

## Future Architecture: Multi-Format, Multi-Platform

### Phase 1: Class Hierarchy Refactoring (Infrastructure)
**Status**: Planned  
**Effort**: 2-3 hours  
**Priority**: Medium (improves maintainability)

#### Goal
Replace URL detection with proper scraper class hierarchy:

```
Scraper (abstract base)
├── StepstoneScraper
├── LinkedInScraper
│   ├── LinkedInCollectionScraper
│   └── LinkedInDirectScraper
├── XINGScraper (future)
├── IndeedScraper (future)
└── GlassdoorScraper (future)
```

#### Benefits
- ✅ Explicit handling of each URL format
- ✅ Optimized selectors per format/platform
- ✅ No fallback failures (each scraper knows its format)
- ✅ Clear error messages and debugging
- ✅ Scales easily to new platforms
- ✅ Better test organization

#### Implementation Outline
1. Create `Scraper` abstract base class with:
   - `can_handle(url)` - route URLs to correct scraper
   - `scrape(url)` - returns normalized `job_data`
   - Field extraction methods (can be overridden per scraper)

2. Create scraper classes:
   - Refactor existing Stepstone scraper to inherit from `Scraper`
   - Create `LinkedInScraper` base for common LinkedIn logic
   - Create `LinkedInCollectionScraper` for current implementation
   - Create `LinkedInDirectScraper` for direct view URLs

3. Create `ScraperFactory`:
   - Takes URL, returns appropriate scraper instance
   - Replace current `detect_job_source()` logic

4. Update `main.py`:
   - Use `ScraperFactory` instead of if/elif platform detection
   - Maintain backward compatibility with existing workflow

#### Backward Compatibility
- All existing tests continue to pass
- `job_data` format unchanged
- `main.py` interface unchanged
- Gradual migration (Phase 1 is architecture only)

---

### Phase 2: Field Confidence & Metadata (Infrastructure)
**Status**: Planned  
**Effort**: 2-3 hours  
**Priority**: Medium (improves data quality transparency)

#### Goal
Add reliability information to difficult-to-extract fields.

#### The Problem
Some fields are hard to extract accurately:
1. **Company address** - Often missing or incomplete from job posting
2. **Publication date** - Rarely visible (especially LinkedIn)
3. **Contact person** - Almost never in job posting
4. **Career portal URL** - Not always linked
5. **Company career portal job URL** - Often unavailable

#### Solution
Add confidence levels to track where each field came from and how reliable it is:

```python
@dataclass
class FieldExtraction:
    value: Optional[str]
    confidence: float  # 0.0 - 1.0
    source: str  # "sidebar", "description_text", "career_portal", "lookup"
    method: str  # How it was extracted
```

#### Example
```python
job_data = {
    'company_name': 'Example Corp',
    'job_title': 'Senior Engineer',
    'company_address': FieldExtraction(
        value='123 Main St, Berlin',
        confidence=0.5,  # Found in description (uncertain)
        source='description_regex'
    ),
    'career_portal_url': FieldExtraction(
        value='https://example.com/careers',
        confidence=0.2,  # Estimated from domain (likely wrong)
        source='domain_estimation'
    ),
}
```

#### Implementation Outline
1. Create `FieldExtraction` dataclass
2. Add to `job_data` schema (as optional fields initially)
3. Update each scraper to return `FieldExtraction` for difficult fields
4. Add tests for confidence levels per scraper
5. Update Trello integration to show confidence indicators

#### Backward Compatibility
- Make `FieldExtraction` optional (existing code doesn't break)
- Fall back to plain strings if not present
- Gradual migration per field

---

### Phase 3: Career Portal Enrichment (Feature)
**Status**: Planned  
**Effort**: 3-4 hours  
**Priority**: High (solves difficult fields)

#### Goal
Extract additional information from company career portals to improve data quality.

#### The Challenge
Many fields are only available on the company's career portal:
- Actual company address (vs. guessed)
- Publication date (with real date, not "3 days ago")
- Contact person (hiring manager)
- Job posting URL on their portal (for backtracking)

#### Solution Strategy
1. Extract/estimate company career portal URL
2. Scrape company portal to find same job posting
3. Extract richer data from portal
4. Merge with LinkedIn/Stepstone data, preferring higher-confidence sources

#### Confidence Hierarchy
```
Field: Company Address
├── Career Portal: 0.95 (official source)
├── Stepstone sidebar: 0.75 (usually accurate)
├── LinkedIn description regex: 0.50 (pattern matching)
├── Estimated from domain: 0.20 (likely wrong)
└── Not found: 0.00

Field: Publication Date
├── Career Portal metadata: 0.90 (official date)
├── Stepstone "posted X days ago": 0.40 (relative)
├── LinkedIn (not available): 0.00
└── Not found: 0.00
```

#### Implementation Outline
1. Create `CareerPortalScraper` class
2. Add `extract_career_portal_url()` for each job scraper
3. Search company portal for matching job posting
4. Extract additional fields from portal
5. Merge data with confidence preference
6. Cache results (same company = reuse portal data)

#### Example
```python
# Start with LinkedIn data
job_data = scrape_linkedin_job(url)
# confidence: company_address=0.5 from description

# Enrich from career portal
enriched = enrich_from_career_portal(job_data)
# Now: company_address=0.95 from portal, with street address
```

---

### Phase 4: Additional Platforms (Expansion)
**Status**: Planned  
**Effort**: 1-2 hours per platform  
**Priority**: Low (when needed)

Once Phase 1 architecture is in place, adding new platforms is straightforward:

```python
class XINGScraper(Scraper):
    def can_handle(self, url: str) -> bool:
        return "xing.com" in url
    
    def scrape(self, url: str) -> JobData:
        # Implement XING-specific logic
        pass

class IndeedScraper(Scraper):
    def can_handle(self, url: str) -> bool:
        return "indeed.com" in url
    
    def scrape(self, url: str) -> JobData:
        # Implement Indeed-specific logic
        pass
```

### Supported Platforms (Future Roadmap)
- ✅ Stepstone (v0.1 - stable)
- ✅ LinkedIn Collection (v0.1 - new)
- 📋 LinkedIn Direct (v0.2 - infrastructure phase)
- 📋 XING (v0.3)
- 📋 Indeed (v0.4)
- 📋 Glassdoor (v0.5)
- 📋 Company career portals (v0.3+)

---

## Design Principles

### 1. Single Responsibility
Each scraper handles ONE format/platform. No fallbacks.

### 2. Confidence Over Perfection
Better to say "address is 50% confident" than to guess incorrectly.

### 3. Gradual Enhancement
Start simple (Phase 1), add features over time (Phases 2-4).

### 4. Backward Compatibility
Old code continues to work. New features are additive.

### 5. Testability
Each scraper has its own tests. Easy to debug failures.

### 6. Maintainability
Clear class hierarchy. Easy for team to add new scrapers.

---

## Migration Path

### v0.1 (Current)
```python
# main.py
if 'linkedin' in url:
    job_data = scrape_linkedin_job(url)
elif 'stepstone' in url:
    job_data = scrape_stepstone_job(url)
```

### v0.2+ (After Phase 1)
```python
# main.py
scraper = ScraperFactory.get_scraper(url)
job_data = scraper.scrape(url)
```

### v0.3+ (After Phase 2-3)
```python
# main.py
scraper = ScraperFactory.get_scraper(url)
job_data = scraper.scrape(url)
enriched_data = enrich_from_career_portal(job_data)
# job_data now has confidence levels
```

---

## Success Criteria

### Phase 1 ✅ (Architecture)
- [ ] All existing tests pass
- [ ] Both Stepstone and LinkedIn work
- [ ] Both LinkedIn URL formats work (collection + direct)
- [ ] No breaking changes to `job_data` or `main.py` interface
- [ ] Code is cleaner and more maintainable

### Phase 2 ✅ (Confidence)
- [ ] Field confidence tracked for all job data
- [ ] Tests verify confidence levels per scraper
- [ ] Documentation clear about data quality per field

### Phase 3 ✅ (Enrichment)
- [ ] Company address improves from career portal
- [ ] Publication dates extracted from portal
- [ ] Contact persons extracted from portal
- [ ] Tests verify enrichment works

### Phase 4 ✅ (Expansion)
- [ ] 3+ additional platforms supported
- [ ] Same quality as original scrapers
- [ ] New platforms take < 1 hour to add

---

## Timeline Recommendation

| Phase | Work | Time | Depends On |
|-------|------|------|-----------|
| 1 | Architecture refactoring | 2-3h | Nothing |
| 2 | Confidence metadata | 2-3h | Phase 1 |
| 3 | Career portal enrichment | 3-4h | Phase 2 |
| 4 | New platforms | 1-2h each | Phase 1 |

**Recommended approach:**
- Do Phase 1 soon (infrastructure, enables everything else)
- Do Phase 2 when quality matters (track field reliability)
- Do Phase 3 when difficult fields are critical (boost address quality)
- Do Phase 4 as new platforms are requested

---

## Notes

- This document describes the **infrastructure roadmap** after v0.1 release
- v0.1 is complete and production-ready
- Future phases are additive (no breaking changes)
- Architecture is designed for team collaboration
- Each phase can be done independently after Phase 1
