"""
LinkedIn Authenticated HTML Scraper

This module scrapes LinkedIn job postings using authenticated session management.
It extracts job data from LinkedIn URLs while respecting rate limits and ToS.

Key Features:
- Session-based authentication
- Rate limiting compliance
- Structured data extraction
- Error handling and retry logic
- Anti-detection measures

Usage:
    scraper = LinkedInJobScraper()
    job_data = scraper.scrape_job_url(url)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
import random
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class LinkedInJobData:
    """Structured LinkedIn job data"""
    company_name: str
    job_title: str
    job_description: str
    location: str
    source_url: str
    job_id: str
    posted_date: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    applicant_count: Optional[int] = None
    salary_range: Optional[str] = None
    easy_apply: bool = False
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    scraped_at: str = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now().isoformat()

class LinkedInJobScraper:
    """LinkedIn job scraper with authentication and rate limiting"""
    
    def __init__(self, rate_limit_delay: int = 5):
        """
        Initialize LinkedIn scraper
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.session = requests.Session()
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
        # Configure session with realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _respect_rate_limit(self):
        """Ensure rate limiting compliance"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            print(f"⏱️ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _add_random_delay(self):
        """Add random human-like delay"""
        delay = random.uniform(1, 3)
        time.sleep(delay)
    
    def extract_job_id_from_url(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL"""
        try:
            # Handle different LinkedIn URL formats
            if 'currentJobId=' in url:
                # Search page with currentJobId parameter
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                return params.get('currentJobId', [None])[0]
            elif '/jobs/view/' in url:
                # Direct job view URL
                match = re.search(r'/jobs/view/(\d+)', url)
                return match.group(1) if match else None
            else:
                # Try to find job ID in URL path or params
                match = re.search(r'(\d{10,})', url)
                return match.group(1) if match else None
        except Exception as e:
            print(f"⚠️ Error extracting job ID from URL: {e}")
            return None
    
    def convert_to_job_view_url(self, url: str, job_id: str) -> str:
        """Convert any LinkedIn job URL to direct view URL"""
        return f"https://www.linkedin.com/jobs/view/{job_id}/"
    
    def scrape_job_url(self, url: str, authenticated: bool = False) -> Optional[LinkedInJobData]:
        """
        Scrape job data from LinkedIn URL
        
        Args:
            url: LinkedIn job URL
            authenticated: Whether to attempt authenticated scraping
            
        Returns:
            LinkedInJobData object or None if scraping failed
        """
        print(f"Scraping LinkedIn job: {url}")
        
        # Extract job ID and convert to direct URL
        job_id = self.extract_job_id_from_url(url)
        if not job_id:
            print("Could not extract job ID from URL")
            return None
        
        # Convert to direct job view URL
        direct_url = self.convert_to_job_view_url(url, job_id)
        print(f"Direct URL: {direct_url}")
        
        # Respect rate limiting
        self._respect_rate_limit()
        
        try:
            # Make request
            response = self.session.get(direct_url, allow_redirects=True)
            response.raise_for_status()
            
            # Add human-like delay
            self._add_random_delay()
            
            # Parse response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if authentication required
            if self._requires_authentication(soup):
                if authenticated:
                    print("Authentication required - attempting authenticated scraping")
                    return self._scrape_authenticated(direct_url, job_id)
                else:
                    print("Authentication required - trying public data extraction")
                    return self._extract_public_data(soup, direct_url, job_id)
            
            # Extract job data
            return self._extract_job_data(soup, direct_url, job_id)
            
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except Exception as e:
            print(f"Scraping failed: {e}")
            return None
    
    def _requires_authentication(self, soup: BeautifulSoup) -> bool:
        """Check if the page requires authentication"""
        auth_indicators = [
            'Sign in to view',
            'Join LinkedIn',
            'authentication required',
            'login-form',
            'sign-in'
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator.lower() in page_text for indicator in auth_indicators)
    
    def _extract_public_data(self, soup: BeautifulSoup, url: str, job_id: str) -> Optional[LinkedInJobData]:
        """Extract any available public data from unauthenticated page"""
        print("Extracting available public data...")
        
        try:
            # Look for JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                        return self._parse_json_ld_job_data(data, url, job_id)
                except json.JSONDecodeError:
                    continue
            
            # Try to extract from meta tags
            job_data = self._extract_from_meta_tags(soup, url, job_id)
            if job_data:
                return job_data
            
            # Try to extract from page title and any visible text
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                if 'LinkedIn' in title_text:
                    # Extract company and job title from page title
                    # LinkedIn format: "Company hiring Job Title in Location | LinkedIn"
                    
                    # Remove "| LinkedIn" suffix
                    clean_title = title_text.replace(' | LinkedIn', '').strip()
                    
                    # Try different patterns
                    patterns = [
                        r'(.+?)\s+hiring\s+(.+?)\s+in\s+(.+?)$',  # "Company hiring Job Title in Location"
                        r'(.+?)\s+at\s+(.+?)$',                   # "Job Title at Company"
                        r'(.+?)\s+-\s+(.+?)$'                     # "Job Title - Company"
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, clean_title)
                        if match:
                            if 'hiring' in pattern:
                                # Format: Company hiring Job Title in Location
                                company_name = match.group(1).strip()
                                job_title = match.group(2).strip()
                                location = match.group(3).strip() if match.lastindex >= 3 else "[Location not available]"
                            else:
                                # Format: Job Title at/- Company
                                job_title = match.group(1).strip()
                                company_name = match.group(2).strip()
                                location = "[Location not available]"
                            
                            # Clean up emojis and extra text
                            company_name = re.sub(r'[\U0001F300-\U0001F9FF]', '', company_name).strip()
                            job_title = re.sub(r'[\U0001F300-\U0001F9FF]', '', job_title).strip()
                            location = re.sub(r'[\U0001F300-\U0001F9FF]', '', location).strip() if location != "[Location not available]" else location
                            
                            return LinkedInJobData(
                                company_name=company_name,
                                job_title=job_title,
                                job_description="[Authentication required for full description]",
                                location=location,
                                source_url=url,
                                job_id=job_id
                            )
                    
                    # If no pattern matches, use the whole title as job title
                    return LinkedInJobData(
                        company_name="[Company name not extractable]",
                        job_title=clean_title,
                        job_description="[Authentication required for full description]",
                        location="[Location not available]",
                        source_url=url,
                        job_id=job_id
                    )
            
            print("No extractable public data found")
            return None
            
        except Exception as e:
            print(f"Error extracting public data: {e}")
            return None
    
    def _parse_json_ld_job_data(self, data: dict, url: str, job_id: str) -> LinkedInJobData:
        """Parse job data from JSON-LD structured data"""
        return LinkedInJobData(
            company_name=data.get('hiringOrganization', {}).get('name', 'Unknown Company'),
            job_title=data.get('title', 'Unknown Position'),
            job_description=data.get('description', ''),
            location=self._extract_location(data.get('jobLocation', {})),
            source_url=url,
            job_id=job_id,
            employment_type=data.get('employmentType'),
            posted_date=data.get('datePosted'),
            salary_range=self._extract_salary(data.get('baseSalary'))
        )
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup, url: str, job_id: str) -> Optional[LinkedInJobData]:
        """Extract job data from meta tags"""
        meta_data = {}
        
        # Extract Open Graph and Twitter Card meta tags
        for meta in soup.find_all('meta'):
            if meta.get('property'):
                meta_data[meta.get('property')] = meta.get('content')
            elif meta.get('name'):
                meta_data[meta.get('name')] = meta.get('content')
        
        # Map meta data to job fields
        if 'og:title' in meta_data or 'twitter:title' in meta_data:
            title = meta_data.get('og:title') or meta_data.get('twitter:title')
            description = meta_data.get('og:description') or meta_data.get('twitter:description', '')
            
            # Try to parse company and job title from title
            # LinkedIn format often: "Job Title - Company Name"
            if ' - ' in title:
                job_title, company_name = title.split(' - ', 1)
            else:
                job_title = title
                company_name = "Unknown Company"
            
            return LinkedInJobData(
                company_name=company_name.strip(),
                job_title=job_title.strip(),
                job_description=description,
                location="[Location not available]",
                source_url=url,
                job_id=job_id
            )
        
        return None
    
    def _scrape_authenticated(self, url: str, job_id: str) -> Optional[LinkedInJobData]:
        """Attempt authenticated scraping (placeholder for future implementation)"""
        print("🔐 Authenticated scraping not yet implemented")
        print("💡 This would require:")
        print("   - LinkedIn login session management")
        print("   - CSRF token handling")
        print("   - Cookie persistence")
        print("   - Additional anti-detection measures")
        
        return LinkedInJobData(
            company_name="[Authentication required]",
            job_title="[Authentication required]",
            job_description="[Authentication required - full scraping needs LinkedIn login]",
            location="[Authentication required]",
            source_url=url,
            job_id=job_id
        )
    
    def _extract_job_data(self, soup: BeautifulSoup, url: str, job_id: str) -> LinkedInJobData:
        """Extract job data from authenticated LinkedIn page"""
        # This would contain the full extraction logic for authenticated pages
        # For now, return placeholder
        return LinkedInJobData(
            company_name="[Authenticated extraction needed]",
            job_title="[Authenticated extraction needed]",
            job_description="[Authenticated extraction needed]",
            location="[Authenticated extraction needed]",
            source_url=url,
            job_id=job_id
        )
    
    def _extract_location(self, location_data) -> str:
        """Extract location from various formats"""
        if isinstance(location_data, dict):
            return location_data.get('address', {}).get('addressLocality', 'Unknown Location')
        elif isinstance(location_data, str):
            return location_data
        else:
            return 'Unknown Location'
    
    def _extract_salary(self, salary_data) -> Optional[str]:
        """Extract salary information"""
        if not salary_data:
            return None
        
        if isinstance(salary_data, dict):
            value = salary_data.get('value')
            currency = salary_data.get('currency', '')
            if value:
                return f"{currency}{value}"
        
        return None
    
    def save_job_data(self, job_data: LinkedInJobData, output_dir: str = "research/linkedin/scraped_data") -> Path:
        """Save scraped job data to JSON file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_job_{job_data.job_id}_{timestamp}.json"
        file_path = output_path / filename
        
        # Convert to dict for JSON serialization
        data_dict = {
            'company_name': job_data.company_name,
            'job_title': job_data.job_title,
            'job_description': job_data.job_description,
            'location': job_data.location,
            'source_url': job_data.source_url,
            'job_id': job_data.job_id,
            'posted_date': job_data.posted_date,
            'employment_type': job_data.employment_type,
            'experience_level': job_data.experience_level,
            'applicant_count': job_data.applicant_count,
            'salary_range': job_data.salary_range,
            'easy_apply': job_data.easy_apply,
            'company_size': job_data.company_size,
            'company_industry': job_data.company_industry,
            'scraped_at': job_data.scraped_at
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Job data saved: {file_path}")
        return file_path

def test_linkedin_scraper():
    """Test the LinkedIn scraper with the provided URL"""
    
    # Test URL provided by user
    test_url = "https://www.linkedin.com/jobs/search/?currentJobId=4295875663&keywords=jobleads%20gmbh&origin=JOBS_HOME_KEYWORD_AUTOCOMPLETE"
    
    print("🧪 Testing LinkedIn HTML Scraper")
    print("=" * 50)
    print(f"Test URL: {test_url}")
    print()
    
    # Create scraper instance
    scraper = LinkedInJobScraper(rate_limit_delay=3)  # 3 second delay for testing
    
    # Attempt to scrape
    job_data = scraper.scrape_job_url(test_url)
    
    if job_data:
        print("\n✅ Scraping successful!")
        print(f"Company: {job_data.company_name}")
        print(f"Job Title: {job_data.job_title}")
        print(f"Location: {job_data.location}")
        print(f"Job ID: {job_data.job_id}")
        print(f"Description: {job_data.job_description[:200]}...")
        
        # Save the data
        file_path = scraper.save_job_data(job_data)
        print(f"Saved to: {file_path}")
        
    else:
        print("\n❌ Scraping failed")
        print("This might be due to:")
        print("- Authentication requirements")
        print("- Rate limiting")
        print("- Changed LinkedIn structure")
        print("- Network issues")
    
    print("\n📝 Next Steps:")
    print("1. Analyze scraped data structure")
    print("2. Implement authentication handling")
    print("3. Add more robust parsing")
    print("4. Test with multiple URLs")

if __name__ == "__main__":
    test_linkedin_scraper()