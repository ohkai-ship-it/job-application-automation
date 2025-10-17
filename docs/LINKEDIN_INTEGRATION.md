# LinkedIn Integration: Simple HTML Scraping

## Approach

Instead of complex API reverse engineering, we use simple HTML scraping:

1. Extract job ID from LinkedIn URLs
2. Convert to direct job view URL
3. Parse page title for company/job/location info
4. Return in standard job_data format

## Implementation

See `src/linkedin_scraper.py` - simple function that works with existing workflow.

## Example

```python
from src.linkedin_scraper import scrape_linkedin_job

url = "https://www.linkedin.com/jobs/search/?currentJobId=4295875663..."
job_data = scrape_linkedin_job(url)
# Returns standard job_data dict
```

## Integration

Will be integrated into main workflow to handle LinkedIn URLs alongside Stepstone URLs.
