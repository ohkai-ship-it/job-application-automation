# Job Scraper Architecture & Abstraction Plan

## Your Proposed Architecture ✅

```
Scraper (base class)
├── StepstoneScraper
├── LinkedInScraper
│   ├── LinkedInCollectionScraper (recommended/?currentJobId=XXX)
│   └── LinkedInDirectScraper (jobs/view/XXX/)
├── OtherPlatform1Scraper
└── OtherPlatform2Scraper
```

**Why this is superior to fallbacks:**
- ✅ Explicit handling of each format
- ✅ Optimized selectors per format
- ✅ No unnecessary retries
- ✅ Clear error messages
- ✅ Easy to debug which format failed
- ✅ Scales to many platforms
- ✅ Tests per scraper type

---

## The Difficult Fields Problem

You've identified the **core challenge**: some fields are platform/format specific.

### The 5 Difficult Fields

1. **Company Address** - Where does it live?
   - Stepstone: Sometimes in sidebar, sometimes in description
   - LinkedIn Collection: In description text
   - LinkedIn Direct: Different description structure
   - Career portal: May have actual address (better quality)

2. **Publication Date** - Often missing!
   - Stepstone: Sometimes shows "posted 3 days ago"
   - LinkedIn: No visible date on job posting
   - Career portal: Might have actual date

3. **Contact Person** - Rarely in job posting
   - Usually ONLY on company career portal
   - Sometimes in job description ("contact X at...")
   - Stepstone: Sometimes in company section

4. **Career Portal URL** - Need to derive/find
   - Stepstone: Sometimes linked
   - LinkedIn: Not available (need to estimate or lookup)
   - Career portal: Need to find company website first

5. **Company Career Portal Job URL** - Separate from job posting URL
   - Different from LinkedIn/Stepstone posting URL
   - Often has more info (address, person, requirements)
   - Requires domain knowledge (knowing company's career site)

---

## Solution Strategy: Confidence Levels

Instead of trying to extract everything from every platform, use a **confidence-based approach**:

### Concept: Field Extraction Confidence

```python
class FieldExtraction:
    """Represents an extracted field with confidence metadata"""
    value: str
    confidence: float  # 0.0 - 1.0
    source: str  # Where it came from (e.g., "description_text", "sidebar", "career_portal")
    platform: str  # "stepstone", "linkedin_collection", "linkedin_direct"
```

### Confidence Levels by Platform

```
Field: Company Address
├── LinkedIn Direct: LOW (0.3) - might be in description
├── LinkedIn Collection: MEDIUM (0.5) - better text extraction
├── Stepstone: MEDIUM-HIGH (0.6) - sometimes in sidebar
├── Career Portal: HIGH (0.9) - usually has official address
└── Manual/Lookup: HIGHEST (1.0)

Field: Publication Date
├── LinkedIn: VERY LOW (0.1) - not visible
├── Stepstone: LOW (0.3) - "posted X days ago"
├── Career Portal: MEDIUM (0.6) - might have actual date
└── Manual/Lookup: HIGHEST (1.0)

Field: Contact Person
├── Job Posting: VERY LOW (0.1) - rarely included
├── Career Portal: MEDIUM (0.5) - sometimes listed
├── Manual/Lookup: HIGHEST (1.0)
└── Company Research: MEDIUM (0.6)

Field: Career Portal URL
├── Estimated (domain): LOW (0.2) - often wrong
├── Found via search: MEDIUM (0.6) - uncertain
├── Provided by job site: HIGH (0.8)
└── Manual: HIGHEST (1.0)
```

---

## Proposed Class Hierarchy & Strategy

### 1. Base Scraper Class

```python
class Scraper(ABC):
    """Abstract base scraper for all job platforms"""
    
    def __init__(self):
        self.platform_name: str  # "stepstone", "linkedin", etc.
        self.variant_name: str  # "collection", "direct", etc.
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this scraper handles the URL"""
        pass
    
    @abstractmethod
    def scrape(self, url: str) -> JobData:
        """Main scraping method - returns normalized job_data"""
        pass
    
    # Shared extraction helpers (can be overridden)
    def extract_company_address(self, soup/page) -> FieldExtraction:
        """Extract company address with confidence level"""
        raise NotImplementedError("Override in subclass")
    
    def extract_publication_date(self, soup/page) -> FieldExtraction:
        """Extract publication date with confidence level"""
        raise NotImplementedError("Override in subclass")
    
    def extract_contact_person(self, soup/page) -> FieldExtraction:
        """Extract contact person with confidence level"""
        raise NotImplementedError("Override in subclass")
    
    def extract_career_portal_url(self, job_data) -> FieldExtraction:
        """Extract or derive career portal URL"""
        raise NotImplementedError("Override in subclass")
    
    def extract_company_career_job_url(self, job_data) -> FieldExtraction:
        """Extract job URL on company career portal"""
        raise NotImplementedError("Override in subclass")
    
    def _build_job_data(self, extracted_fields) -> JobData:
        """Normalize all fields into standard job_data format"""
        # Common logic for all scrapers
        pass
```

### 2. LinkedIn Collection Scraper

```python
class LinkedInCollectionScraper(Scraper):
    """Scrapes LinkedIn jobs from collection view"""
    
    platform_name = "linkedin"
    variant_name = "collection"
    
    def can_handle(self, url: str) -> bool:
        return "collections/recommended" in url or "currentJobId" in url
    
    def scrape(self, url: str) -> JobData:
        job_id = self.extract_job_id(url)
        
        # Use Playwright for this specific format
        description = self._extract_via_playwright_collection(job_id)
        
        # Extract difficult fields specific to this format
        address = self.extract_company_address(soup)  # LOW confidence
        pub_date = self.extract_publication_date(soup)  # VERY LOW
        contact = self.extract_contact_person(soup)  # VERY LOW
        portal_url = self.extract_career_portal_url(job_data)  # LOW (estimate)
        
        return self._build_job_data({
            'company_name': company,
            'job_title': title,
            'job_description': description,
            'location': location,
            'company_address': address,  # Include confidence
            'publication_date': pub_date,  # Include confidence
            'contact_person': contact,  # Include confidence
            'career_portal_url': portal_url,  # Include confidence
            'source_url': url,
            'platform': self.platform_name,
            'variant': self.variant_name,
        })
```

### 3. LinkedIn Direct Scraper

```python
class LinkedInDirectScraper(Scraper):
    """Scrapes LinkedIn jobs from direct view"""
    
    platform_name = "linkedin"
    variant_name = "direct"
    
    def can_handle(self, url: str) -> bool:
        return "/jobs/view/" in url and "linkedin.com" in url
    
    def scrape(self, url: str) -> JobData:
        # Different Playwright strategy for direct view
        description = self._extract_via_playwright_direct(url)
        
        # Different selectors for this format
        address = self.extract_company_address_direct(soup)
        
        # ... rest of extraction
        
        return self._build_job_data({...})
```

### 4. Stepstone Scraper (Refactored)

```python
class StepstoneScraper(Scraper):
    """Existing Stepstone scraper, refactored to inherit"""
    
    platform_name = "stepstone"
    variant_name = "standard"
    
    def can_handle(self, url: str) -> bool:
        return "stepstone" in url
    
    def scrape(self, url: str) -> JobData:
        # Use existing Stepstone logic, but return FieldExtractions
        # Now consistently handles difficult fields
        pass
```

---

## Handling Difficult Fields: Strategy

### For Each Difficult Field, Use This Hierarchy:

```python
def extract_field_with_fallback(self, job_data: JobData) -> FieldExtraction:
    """
    Try multiple strategies, return best confidence level found
    """
    attempts = [
        self._extract_from_job_posting(),  # Primary (LOW-MEDIUM confidence)
        self._extract_from_description_text(),  # Secondary (LOW confidence)
        self._estimate_or_lookup(),  # Tertiary (varies)
        self._mark_unavailable(),  # Fallback (confidence: 0)
    ]
    
    for attempt in attempts:
        if attempt.confidence > 0:
            return attempt
    
    return FieldExtraction(value=None, confidence=0, source="unavailable")
```

### Field-Specific Strategies:

#### 1. Company Address
```python
def extract_company_address(self, soup) -> FieldExtraction:
    """
    Strategy:
    1. Look in sidebar/company section (if available)
    2. Search description for address patterns (Street, Postal, City)
    3. Lookup from career portal (if we have URL)
    4. Return "Not available"
    """
    strategies = [
        ('sidebar', self._extract_from_sidebar),
        ('description_regex', self._extract_from_description),
        ('career_portal_lookup', self._lookup_from_career_portal),
        ('company_research', self._research_company),
    ]
    
    for name, strategy in strategies:
        result = strategy()
        if result.value:
            result.source = name
            return result
    
    return FieldExtraction(None, 0, "unavailable")
```

#### 2. Publication Date
```python
def extract_publication_date(self, soup) -> FieldExtraction:
    """
    Strategy:
    1. Look for date meta tag
    2. Parse "posted X days ago" text
    3. Check career portal (if available)
    4. Return None with confidence 0
    """
    # Most job sites don't show this clearly
    # LinkedIn especially doesn't
    # Return LOW confidence when found
```

#### 3. Contact Person
```python
def extract_contact_person(self, soup) -> FieldExtraction:
    """
    Strategy:
    1. Search description for "contact X at" patterns
    2. Look for hiring manager name/email
    3. Check career portal (if available)
    4. Return None
    """
    # Rarely available in job posting
    # Career portal might have it
```

#### 4. Career Portal URL
```python
def extract_career_portal_url(self, job_data) -> FieldExtraction:
    """
    Strategy:
    1. Look for link in job posting (HIGH confidence)
    2. Estimate from company name (LOW confidence)
    3. Research company website (MEDIUM confidence)
    4. Return None
    """
    # This is critical - try to find real portal
    # Not just estimate
```

#### 5. Company Career Portal Job URL
```python
def extract_company_career_job_url(self, job_data) -> FieldExtraction:
    """
    Strategy:
    1. Look for link in job posting (HIGH confidence if found)
    2. Try to locate same job on company portal (MEDIUM confidence)
    3. Return None
    """
    # Often not available from job posting
    # Would need to search company portal
```

---

## Implementation Plan: Phased Approach

### Phase 1: Core Architecture (Priority: HIGH)
**Effort: 2-3 hours**

Create base class and refactor existing scrapers:
- [ ] Create `Scraper` base class
- [ ] Create `FieldExtraction` data class
- [ ] Refactor `StepstoneScraper` to inherit
- [ ] Create `LinkedInScraper` base class
- [ ] Create `LinkedInCollectionScraper`
- [ ] Create `LinkedInDirectScraper`
- [ ] Create `ScraperFactory` to route URLs to correct scraper
- [ ] Update `main.py` to use factory

**Deliverable:** All existing tests pass, both LinkedIn formats work

### Phase 2: Difficult Fields Infrastructure (Priority: MEDIUM)
**Effort: 2-3 hours**

Implement field extraction with confidence:
- [ ] Add `FieldExtraction` to job_data schema
- [ ] Implement address extraction per scraper
- [ ] Implement publication date extraction
- [ ] Implement contact person extraction
- [ ] Implement career portal URL extraction
- [ ] Add tests for each field type

**Deliverable:** Structured metadata about field reliability

### Phase 3: Career Portal Integration (Priority: MEDIUM)
**Effort: 3-4 hours**

Actually extract from company career portals:
- [ ] Scrape company career portal for additional info
- [ ] Link back to original job posting URL
- [ ] Extract address from portal
- [ ] Extract contact info from portal
- [ ] Cache results (same company)

**Deliverable:** Richer job data from multiple sources

### Phase 4: Future Platforms (Priority: LOW)
**Effort: 1-2 hours per platform**

Add more scrapers easily:
- [ ] Create `XIINGScraper`
- [ ] Create `GlassdoorScraper`
- [ ] Create `IndeedScraper`
- [ ] Create custom platform support

**Deliverable:** Extensible system for new platforms

---

## Data Schema Evolution

### Current job_data:
```python
{
    'company_name': str,
    'job_title': str,
    'job_description': str,
    'location': str,
    'source_url': str,
    'company_address': str,
    'career_page_link': str,
}
```

### Enhanced job_data (with Phase 2):
```python
{
    'company_name': str,
    'job_title': str,
    'job_description': str,
    'location': str,
    'source_url': str,
    
    # Difficult fields with confidence
    'company_address': FieldExtraction,  # value, confidence, source
    'publication_date': FieldExtraction,
    'contact_person': FieldExtraction,
    'career_portal_url': FieldExtraction,
    'company_career_job_url': FieldExtraction,
    'career_page_link': FieldExtraction,
    
    # Metadata
    'platform': str,  # "stepstone", "linkedin", "xing"
    'variant': str,  # "collection", "direct"
    'extraction_timestamp': datetime,
}
```

### FieldExtraction Class:
```python
@dataclass
class FieldExtraction:
    value: Optional[str] = None
    confidence: float = 0.0  # 0.0 - 1.0
    source: str = "unknown"  # Where it came from
    method: str = "unknown"  # How it was extracted
    notes: str = ""  # Any additional info
    
    def is_reliable(self, threshold: float = 0.7) -> bool:
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        return f"{self.value} (confidence: {self.confidence:.0%}, source: {self.source})"
```

---

## Benefits of This Architecture

### Immediate
✅ Clear separation of concerns  
✅ Easy to debug (know which scraper/format failed)  
✅ Optimal selectors per format  
✅ No fallback failures  
✅ Transparent about data quality  

### Long-term
✅ Add platforms without affecting existing code  
✅ Share utilities across similar platforms  
✅ Track field extraction quality  
✅ Improve extraction over time per platform  
✅ Easy to add validation/verification steps  

### Testing
✅ Unit tests per scraper  
✅ Tests per field type  
✅ Confidence level assertions  
✅ Easy to mock platforms  

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing tests | Keep job_data backward compatible initially, add metadata as optional fields |
| Performance impact | No impact - direct scraping, no fallbacks |
| Difficult to migrate | Phased approach - do Phase 1 first, keep working before Phase 2 |
| Over-engineering | Start with just routing, add field confidence gradually |

---

## Quick Start: Phase 1 Only (Recommended)

If we just do **Phase 1** (architecture + routing):
- ✅ Both LinkedIn formats work
- ✅ Clean, maintainable code
- ✅ Ready for future expansion
- ✅ All existing tests pass
- ✅ ~2-3 hours of work
- ❌ Fields still not perfect (acceptable for now)

Then later phases can add quality metadata as needed.

---

## Questions/Decisions Needed

1. **Should FieldExtraction be optional or required in job_data?**
   - Option A: Gradual migration (optional in Phase 1, required in Phase 2)
   - Option B: Add immediately (all fields have confidence)

2. **Should we add career portal scraping in Phase 1?**
   - Option A: Phase 1 architecture only (focuses on URL routing)
   - Option B: Include career portal lookup (more complete but more work)

3. **Priority for Phase 3 (career portal)?**
   - Option A: Do it soon (most valuable for difficult fields)
   - Option B: Do other platforms first (Phase 4)

My recommendations:
1. **FieldExtraction**: Gradual (optional first, required later)
2. **Career portal**: Not in Phase 1 (focus on routing)
3. **Phase 3 priority**: HIGH (solves difficult fields)

---

## Recommended Action Plan

```
Week 1:
  Phase 1: Architecture + URL routing (2-3 hours)
    └─ Both LinkedIn formats work
    └─ All tests pass

Week 2:
  Phase 2: Field confidence (2-3 hours)
    └─ Metadata about field reliability
    └─ Better transparency

Week 3:
  Phase 3: Career portal (3-4 hours)
    └─ Extract from company sites
    └─ Richer job data

Future:
  Phase 4: Other platforms
    └─ XING, Glassdoor, Indeed, etc.
```

---

**Shall I proceed with Phase 1 implementation?** This architecture makes sense and is worth doing properly. I can start with the base class and URL routing.
