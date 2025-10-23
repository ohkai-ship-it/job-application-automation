# Scraper Class Structure Refactoring Design

## Current State
- `scraper.py`: ~520 lines of function-based code
  - Main function: `scrape_stepstone_job(url)` → returns `job_data` dict
  - Helper functions: `clean_job_title()`, `split_address()`, `extract_company_address_from_description()`
  - Internal utilities: `find_address_after_company()`, address parsing logic
  
- `linkedin_scraper.py`: ~393 lines of async function-based code
  - Main functions: `extract_job_description_playwright(url)`, `extract_job_description(soup)`, `extract_job_id_from_url(url)`
  - No class structure, purely functional

- `main.py`: Imports `scrape_stepstone_job` function directly
  - Calls: `job_data = scrape_stepstone_job(url)` on line 103

## Design Goals
1. Create professional class-based architecture
2. Maintain backward compatibility with existing API
3. Enable source detection (Stepstone vs LinkedIn vs others)
4. Share common functionality through base class
5. Improve testability and maintainability

## Proposed Class Hierarchy

```
BaseJobScraper (abstract base class)
├── StepstoneScraper
└── LinkedInScraper
```

### BaseJobScraper (abstract)
**Purpose**: Define interface, share common utilities

**Location**: Create in `scraper.py` (or separate `scrapers/base.py`)

**Key Methods**:
```python
class BaseJobScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> Optional[JobData]:
        """Scrape job data from URL"""
        pass
    
    def _get_logger(self) -> Logger:
        """Get logger for this scraper"""
        pass
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format for this scraper"""
        pass
```

**Shared Utilities**:
- `logger` initialization
- HTTP request handling with retries
- Common error handling
- JobData dict template initialization

### StepstoneScraper
**Purpose**: Scrape Stepstone job postings

**Location**: In `scraper.py` as main class

**Current Functions to Convert**:
- `scrape_stepstone_job()` → `scrape(url)` (main method)
- `clean_job_title()` → `_clean_job_title()` (private)
- `split_address()` → `_split_address()` (private)
- `extract_company_address_from_description()` → `_extract_address_from_description()` (private)

**Key Methods**:
```python
class StepstoneScraper(BaseJobScraper):
    async def scrape(self, url: str) -> Optional[JobData]:
        """Main scraping entry point"""
        
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[JsonLD]:
        """Extract JSON-LD structured data"""
        
    def _extract_from_dom(self, soup: BeautifulSoup) -> dict:
        """Fallback DOM-based extraction"""
        
    def _clean_job_title(self, title: str) -> str:
        """Remove gender markers from titles"""
        
    def _extract_address_from_description(self, desc: str) -> Optional[Dict]:
        """Parse address from description text"""
```

### LinkedInScraper
**Purpose**: Scrape LinkedIn job postings using Playwright

**Location**: In `linkedin_scraper.py` as main class

**Current Functions to Convert**:
- `extract_job_description_playwright()` → `_scrape_with_playwright()` (private method called by scrape())
- `extract_job_description()` → `_extract_from_static_html()` (private fallback)
- `extract_job_id_from_url()` → `_extract_job_id()` (private)
- `extract_company()` → `_extract_company()` (private)

**Key Methods**:
```python
class LinkedInScraper(BaseJobScraper):
    async def scrape(self, url: str) -> Optional[JobData]:
        """Main scraping entry point (async)"""
        
    async def _scrape_with_playwright(self, url: str) -> Optional[str]:
        """Render page with Playwright, extract description"""
        
    def _extract_from_static_html(self, html: str) -> Optional[str]:
        """Fallback for static HTML"""
        
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract LinkedIn job ID from URL"""
```

## Return Type: JobData

**Standardized across all scrapers**:
```python
JobData = Dict[str, Any]

# Expected keys (based on current scraper.py):
{
    'company_name': str,
    'company_address': str,
    'company_address_line1': str,
    'company_address_line2': str,
    'job_title': str,
    'job_title_clean': str,
    'location': str,
    'work_mode': str,
    'website_link': str,
    'career_page_link': str,
    'direct_apply_link': str,
    'publication_date': str,
    'job_description': str,
    'contact_person': {'name': str, 'email': str, 'phone': str},
    'scraped_at': str (ISO format),
    'source_url': str,
    'source': str ('stepstone'|'linkedin'|...),
    # LinkedIn specific:
    'linkedin_job_id': str,
    # Stepstone specific:
    'stepstone_job_id': str,
}
```

## Integration Points

### main.py Changes
**Before**:
```python
from scraper import scrape_stepstone_job, save_to_json

# In process_job_posting():
job_data = scrape_stepstone_job(url)
```

**After**:
```python
from scraper import create_scraper
from scrapers.base import BaseJobScraper

# In process_job_posting():
scraper = create_scraper(url)  # Returns StepstoneScraper or LinkedInScraper
job_data = await scraper.scrape(url)  # Async call
```

### Source Detection
**New factory function**:
```python
def create_scraper(url: str) -> BaseJobScraper:
    """Create appropriate scraper based on URL"""
    if 'stepstone' in url.lower():
        return StepstoneScraper()
    elif 'linkedin' in url.lower():
        return LinkedInScraper()
    else:
        raise ValueError(f"Unsupported job source: {url}")
```

## Migration Path

**Phase 1**: Create base class and new class-based scrapers
**Phase 2**: Update main.py to use new scrapers (async handling needed)
**Phase 3**: Test thoroughly with real URLs
**Phase 4**: Keep old function-based API as thin wrapper (for compatibility)
**Phase 5**: Eventually deprecate function-based API

## Async Considerations

**Challenge**: LinkedIn scraper uses async/await (Playwright)
**Solution**: Make all scrapers async-capable
- `BaseJobScraper.scrape()` will be async
- `main.py` process_job_posting() will need async handling
- For Stepstone, async is optional but compatible

**Implementation**:
```python
# In main.py
import asyncio

async def process_job_posting_async(url: str, ...) -> Dict:
    scraper = create_scraper(url)
    job_data = await scraper.scrape(url)
    # ... rest of processing
    return result

# Public interface (backward compatible)
def process_job_posting(url: str, ...) -> Dict:
    return asyncio.run(process_job_posting_async(url, ...))
```

## Backward Compatibility

**Maintain existing functions as thin wrappers**:
```python
# In scraper.py (new implementation)
async def scrape_stepstone_job_async(url: str) -> Optional[JobData]:
    scraper = StepstoneScraper()
    return await scraper.scrape(url)

# Old function-based API (for compatibility)
def scrape_stepstone_job(url: str) -> Optional[JobData]:
    return asyncio.run(scrape_stepstone_job_async(url))
```

This allows gradual migration without breaking existing code.

## Testing Strategy

1. **Unit tests** per scraper class method
2. **Integration tests** with real URLs
3. **Compatibility tests** with existing API consumers
4. **Error handling tests** for network failures, malformed HTML, etc.

## Files to Modify

1. `src/scraper.py` - Add StepstoneScraper class, update old functions
2. `src/linkedin_scraper.py` - Add LinkedInScraper class
3. `src/main.py` - Update scraper imports, make process_job_posting async-capable
4. `src/app.py` - May need minor updates if it directly uses scrapers
5. Create `src/scrapers/base.py` (optional, if keeping separate base class)
6. Create `src/scrapers/__init__.py` (optional, for cleaner imports)

## Success Criteria

- ✅ All functions converted to class methods
- ✅ Base class defines clear interface
- ✅ Tests pass with new class structure
- ✅ main.py properly integrates new scrapers
- ✅ Backward-compatible old API still works
- ✅ Async handling works for both scrapers
- ✅ No functionality lost in refactoring
