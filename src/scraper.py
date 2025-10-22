"""
Job Scraper Module with Class-Based Architecture
Refactored from function-based to class-based for better maintainability and testability.
"""

import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Union
from abc import ABC, abstractmethod
import asyncio

try:
    from .utils.log_config import get_logger
    from .utils.http_utils import request_with_retries
    from .utils.errors import ScraperError
except Exception:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.log_config import get_logger
    from utils.http_utils import request_with_retries
    from utils.errors import ScraperError

# Type aliases for clarity
JobData = Dict[str, Any]
Address = Dict[str, str]
JsonLD = Dict[str, Any]


class BaseJobScraper(ABC):
    """
    Abstract base class for job scrapers.
    Defines the interface and shared utilities for all job scraper implementations.
    """
    
    def __init__(self):
        """Initialize the scraper with logger."""
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    async def scrape(self, url: str) -> Optional[JobData]:
        """
        Scrape job data from the given URL.
        
        Args:
            url: The job posting URL to scrape
            
        Returns:
            Dictionary containing extracted job data or None if scraping failed
        """
        pass
    
    def _create_empty_job_data(self, source_url: str) -> JobData:
        """
        Create an empty job data dictionary with default values.
        
        Args:
            source_url: The source URL being scraped
            
        Returns:
            Initialized job data dictionary
        """
        return {
            'company_name': None,
            'company_address': None,
            'company_address_line1': None,
            'company_address_line2': None,
            'job_title': None,
            'job_title_clean': None,
            'location': None,
            'work_mode': None,
            'website_link': None,
            'career_page_link': None,
            'direct_apply_link': None,
            'publication_date': None,
            'job_description': None,
            'contact_person': {
                'name': None,
                'email': None,
                'phone': None
            },
            'scraped_at': datetime.now().isoformat(),
            'source_url': source_url
        }


class StepstoneScraper(BaseJobScraper):
    """
    Scraper for Stepstone job postings.
    Extracts job data using JSON-LD structured data with DOM fallbacks.
    """
    
    async def scrape(self, url: str) -> Optional[JobData]:
        """
        Scrape a Stepstone job posting and extract key information.
        
        Args:
            url: The URL of the Stepstone job posting
            
        Returns:
            Dictionary containing extracted job information or None if scraping failed
        """
        job_data = self._create_empty_job_data(url)
        
        try:
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            # Fetch the page with retries
            self.logger.info("Fetching URL: %s", url)
            try:
                response = request_with_retries('GET', url, headers=headers, timeout=10)
            except requests.HTTPError as e:
                status = getattr(getattr(e, 'response', None), 'status_code', 'unknown')
                self.logger.error("HTTP error fetching %s (status %s): %s", url, status, str(e))
                raise ScraperError(f"HTTP {status} for {url}") from e
            except requests.RequestException as e:
                self.logger.error("Network error fetching %s: %s", url, e)
                raise ScraperError(f"Network error for {url}") from e

            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            self.logger.debug("Page fetched successfully. Extracting data...")
            
            # Extract Stepstone Job ID from URL
            stepstone_id_match = re.search(r'--(\d+)-inline\.html', url)
            if stepstone_id_match:
                job_data['stepstone_job_id'] = stepstone_id_match.group(1)
                self.logger.debug("Stepstone Job ID: %s", job_data['stepstone_job_id'])
            
            # Extract from JSON-LD (most reliable!)
            json_ld_data = self._extract_from_json_ld(soup)
            
            # 1. Job Title
            if json_ld_data and 'title' in json_ld_data:
                job_data['job_title'] = json_ld_data['title']
                job_data['job_title_clean'] = self._clean_job_title(job_data['job_title'])
            else:
                title_tag = soup.find(attrs={'data-at': 'header-job-title'})
                if title_tag:
                    job_data['job_title'] = title_tag.get_text(strip=True)
                    job_data['job_title_clean'] = self._clean_job_title(job_data['job_title'])
            
            if job_data['job_title']:
                self.logger.debug("Job Title: %s", job_data['job_title'])
                if job_data['job_title_clean'] and job_data['job_title'] != job_data['job_title_clean']:
                    self.logger.debug("  Clean: %s", job_data['job_title_clean'])
            
            # 2. Company Name
            if json_ld_data and 'hiringOrganization' in json_ld_data:
                job_data['company_name'] = json_ld_data['hiringOrganization'].get('name')
            else:
                company_tag = soup.find(attrs={'data-at': 'metadata-company-name'})
                if company_tag:
                    job_data['company_name'] = company_tag.get_text(strip=True)
            
            if job_data['company_name']:
                self.logger.debug("Company: %s", job_data['company_name'])
            
            # 3. Location
            if json_ld_data and 'jobLocation' in json_ld_data:
                location_data = json_ld_data['jobLocation']
                if isinstance(location_data, dict) and 'address' in location_data:
                    address = location_data['address']
                    if isinstance(address, dict):
                        job_data['location'] = address.get('addressLocality', '')
            
            if not job_data['location']:
                location_tag = soup.find(attrs={'data-at': 'metadata-location'})
                if location_tag:
                    job_data['location'] = location_tag.get_text(strip=True)
            
            if job_data['location']:
                self.logger.debug("Location: %s", job_data['location'])
            
            # 4. Work Mode
            work_type_tag = soup.find(attrs={'data-at': 'metadata-work-type'})
            if work_type_tag:
                work_type_text = work_type_tag.get_text(strip=True).lower()
                if 'homeoffice' in work_type_text or 'remote' in work_type_text:
                    if 'hybrid' in work_type_text:
                        job_data['work_mode'] = 'hybrid'
                    else:
                        job_data['work_mode'] = 'remote/homeoffice'
                else:
                    job_data['work_mode'] = 'office'
                self.logger.debug("Work Mode: %s", job_data['work_mode'])
            
            # 5. Publication Date
            if json_ld_data and 'datePosted' in json_ld_data:
                job_data['publication_date'] = json_ld_data['datePosted']
                self.logger.debug("Publication Date: %s", job_data['publication_date'])
            
            # 6. Job Description
            if json_ld_data and 'description' in json_ld_data:
                desc_html = json_ld_data['description']
                desc_soup = BeautifulSoup(desc_html, 'lxml')
                job_data['job_description'] = desc_soup.get_text(separator='\n', strip=True)
                desc_preview = job_data['job_description'][:200] + "..."
                self.logger.debug("Job Description preview: %s", desc_preview)
            
            # 6b. Extract Company Reference Number from job description
            if job_data.get('job_description'):
                ref_patterns = [
                    r'Referenznummer[:\s]+([A-Z0-9\-_/]+)',
                    r'Referenz[:\s]+([A-Z0-9\-_/]+)',
                    r'Job-ID[:\s]+([A-Z0-9\-_/]+)',
                    r'Job ID[:\s]+([A-Z0-9\-_/]+)',
                    r'Kennziffer[:\s]+([A-Z0-9\-_/]+)',
                    r'Stellennummer[:\s]+([A-Z0-9\-_/]+)',
                    r'Reference[:\s]+([A-Z0-9\-_/]+)',
                    r'Req\.?\s*ID[:\s]+([A-Z0-9\-_/]+)',
                    r'Position\s*ID[:\s]+([A-Z0-9\-_/]+)',
                ]
                
                for pattern in ref_patterns:
                    match = re.search(pattern, job_data['job_description'], re.IGNORECASE)
                    if match:
                        job_data['company_job_reference'] = match.group(1).strip()
                        self.logger.debug("Company Reference Number: %s", job_data['company_job_reference'])
                        break
            
            # Also check if it's in JSON-LD
            if json_ld_data and 'identifier' in json_ld_data:
                if not job_data.get('company_job_reference'):
                    ref_value = json_ld_data['identifier']
                    if isinstance(ref_value, dict):
                        ref_value = ref_value.get('value', '')
                    job_data['company_job_reference'] = str(ref_value)
                    self.logger.debug("Company Reference (from JSON-LD): %s", job_data['company_job_reference'])
            
            # 7. Company Address
            if job_data.get('job_description') and job_data.get('company_name'):
                extracted_address = self._extract_address_from_description(
                    job_data['job_description'], 
                    job_data['company_name']
                )
                if extracted_address:
                    job_data['company_address_line1'] = extracted_address['line1']
                    job_data['company_address_line2'] = extracted_address['line2']
                    job_data['company_address'] = f"{extracted_address['line1']}, {extracted_address['line2']}"
                    self.logger.debug("Company Address (from job description): %s", job_data['company_address'])
            
            # Fallback: use jobLocation if no address found in description
            if not job_data.get('company_address'):
                if json_ld_data and 'jobLocation' in json_ld_data:
                    location_data = json_ld_data['jobLocation']
                    if isinstance(location_data, dict) and 'address' in location_data:
                        address = location_data['address']
                        address_parts = []
                        if 'streetAddress' in address:
                            address_parts.append(address['streetAddress'])
                        if 'postalCode' in address:
                            address_parts.append(address['postalCode'])
                        if 'addressLocality' in address:
                            address_parts.append(address['addressLocality'])
                        if 'addressCountry' in address:
                            address_parts.append(address['addressCountry'])
                        
                        if address_parts:
                            job_data['company_address'] = ', '.join(address_parts)
                            lines = self._split_address(address)
                            job_data['company_address_line1'] = lines[0]
                            job_data['company_address_line2'] = lines[1]
                            self.logger.debug("Company Address (from jobLocation): %s", job_data['company_address'])
            
            # 8. Website Link
            real_company_website = None
            
            if json_ld_data and 'hiringOrganization' in json_ld_data:
                org = json_ld_data['hiringOrganization']
                if 'url' in org:
                    url_value = org['url']
                    if 'stepstone.de' not in url_value:
                        real_company_website = url_value
                        job_data['website_link'] = url_value
                        self.logger.debug("Company Website: %s", job_data['website_link'])
            
            # Construct likely company website from company name
            if not real_company_website and job_data.get('company_name'):
                company_clean = job_data['company_name'].lower()
                for suffix in ['gmbh', 'ag', 'se', 'kg', 'ohg', 'gbr', 'ug', 'ev', 'mbh', 'ltd', 'inc', 'llc', 'corp']:
                    company_clean = company_clean.replace(' ' + suffix, '')
                company_clean = re.sub(r'[^a-z0-9]', '', company_clean)
                
                job_data['website_link'] = f"https://www.{company_clean}.de"
                self.logger.debug("Estimated Website: %s", job_data['website_link'])
                real_company_website = job_data['website_link']
            
            # 9. Career Page Link
            if real_company_website and real_company_website.startswith('http'):
                if 'stepstone.de' not in real_company_website:
                    base_url = real_company_website.rstrip('/')
                    job_data['career_page_link'] = f"{base_url}/karriere"
                    self.logger.debug("Career Page (estimated): %s", job_data['career_page_link'])
                    
            # 10. Direct Apply Link
            apply_buttons = soup.find_all(['a', 'button'], string=re.compile('jetzt bewerben|apply now|bewerben', re.I))
            for button in apply_buttons:
                if button.name == 'a' and button.get('href'):
                    href = button['href']
                    if 'stepstone.de' not in href or '/go/' in href:
                        job_data['direct_apply_link'] = href if href.startswith('http') else f'https://{href}'
                        self.logger.debug("Direct Apply Link: %s", job_data['direct_apply_link'])
                        break
            
            # 11. Contact Information
            page_text = soup.get_text()
            
            # Email
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
            emails = [e for e in emails if not any(x in e.lower() for x in ['beispiel', 'example', 'noreply'])]
            if emails:
                job_data['contact_person']['email'] = emails[0]
                self.logger.debug("Contact Email: %s", job_data['contact_person']['email'])
            
            # Phone
            phones = re.findall(r'\+?\d{2,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}', page_text)
            phones = [p for p in phones if len(p.replace(' ', '').replace('-', '')) > 8]
            if phones:
                job_data['contact_person']['phone'] = phones[0].strip()
                self.logger.debug("Contact Phone: %s", job_data['contact_person']['phone'])
            
            self.logger.info("Scraping completed successfully")
            return job_data

        except ScraperError:
            return None
        except Exception as e:
            self.logger.exception("Error parsing page %s: %s", url, e)
            return None
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[JsonLD]:
        """Extract JSON-LD structured data from the page."""
        json_ld_script = soup.find('script', type='application/ld+json')
        if json_ld_script and json_ld_script.string:
            try:
                return json.loads(json_ld_script.string)
            except:
                pass
        return None
    
    def _clean_job_title(self, title: Optional[str]) -> Optional[str]:
        """Remove gender markers from job titles."""
        if not title:
            return title
        
        gender_patterns = [
            r'\(m/w/d\)', r'\(w/m/d\)', r'\(d/m/w\)',
            r'\(m/f/d\)', r'\(f/m/d\)', r'\(gn\)',
            r'\(m/w\)', r'\(w/m\)',
            r'\(all genders\)', r'\(x/w/m\)',
            r'm/w/d', r'w/m/d',
        ]
        
        cleaned = title
        for pattern in gender_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s*-\s*$', '', cleaned)
        cleaned = re.sub(r'^\s*-\s*', '', cleaned)
        return cleaned.strip()
    
    def _split_address(self, address_dict: Address) -> Tuple[str, str]:
        """Split address into two lines for letter formatting."""
        line1 = address_dict.get('streetAddress', '')
        
        parts = []
        if address_dict.get('postalCode'):
            parts.append(address_dict['postalCode'])
        if address_dict.get('addressLocality'):
            parts.append(address_dict['addressLocality'])
        
        line2 = ' '.join(parts)
        return (line1, line2)
    
    def _extract_address_from_description(self, description: str, company_name: str) -> Optional[Dict[str, str]]:
        """Extract company address from job description text."""
        if not description or not company_name:
            return None
        
        lines = description.split('\n')
        
        # Priority 1: Look in priority sections
        priority_sections = ['weitere informationen', 'additional information', 'contact information', 'kontaktinformationen']
        priority_section_start = -1
        
        for i, line in enumerate(lines):
            if any(section in line.lower() for section in priority_sections):
                priority_section_start = i
                break
        
        def find_address_after_company(start_idx, end_idx=None):
            if end_idx is None:
                end_idx = len(lines)
            
            for i in range(start_idx, min(end_idx, len(lines))):
                if company_name.lower() in lines[i].lower():
                    remaining_lines = lines[i+1:min(i+4, end_idx)]
                    
                    street = None
                    postal_city = None
                    
                    for next_line in remaining_lines:
                        next_line = next_line.strip()
                        if not next_line or next_line.startswith('http'):
                            continue
                        
                        postal_match = re.match(r'^(\d{5})\s+(.+)$', next_line)
                        if postal_match:
                            postal_city = next_line
                            break
                        
                        street_patterns = [
                            r'.*(?:straße|strasse|weg|platz|allee|ring|gasse|str\.|street|avenue|road|drive|lane).*\d+',
                            r'^[A-Za-zäöüÄÖÜß\-\s]+\d+',
                        ]
                        
                        for pattern in street_patterns:
                            if re.search(pattern, next_line, re.IGNORECASE):
                                street = next_line
                                break
                    
                    if street and postal_city:
                        return {'line1': street, 'line2': postal_city}
            
            return None
        
        if priority_section_start >= 0:
            address = find_address_after_company(priority_section_start, len(lines))
            if address:
                return address
        
        return find_address_after_company(0, len(lines))


# ===== Backward Compatibility Functions =====
# These functions maintain the old API for existing code

def clean_job_title(title: Optional[str]) -> Optional[str]:
    """
    (DEPRECATED) Remove gender markers from job titles
    Use StepstoneScraper._clean_job_title() instead.
    """
    scraper = StepstoneScraper()
    return scraper._clean_job_title(title)


def split_address(address_dict: Address) -> Tuple[str, str]:
    """
    (DEPRECATED) Split address into two lines
    Use StepstoneScraper._split_address() instead.
    """
    scraper = StepstoneScraper()
    return scraper._split_address(address_dict)


def extract_company_address_from_description(description: str, company_name: str) -> Optional[Dict[str, str]]:
    """
    (DEPRECATED) Extract company address from description
    Use StepstoneScraper._extract_address_from_description() instead.
    """
    scraper = StepstoneScraper()
    return scraper._extract_address_from_description(description, company_name)


async def scrape_stepstone_job_async(url: str) -> Optional[JobData]:
    """
    Async version - new recommended API.
    """
    scraper = StepstoneScraper()
    return await scraper.scrape(url)


def scrape_stepstone_job(url: str) -> Optional[JobData]:
    """
    (LEGACY) Scrape Stepstone job - maintains backward compatibility.
    For async applications, use scrape_stepstone_job_async() instead.
    """
    return asyncio.run(scrape_stepstone_job_async(url))


def save_to_json(data: JobData, filename: Union[str, Path]) -> None:
    """Save scraped data to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Test/Example Usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        test_url = "https://www.stepstone.de/stellenangebote--Program-Manager-Aachen-Duesseldorf-bundesweit-Utimaco-GmbH--12311219-inline.html"
        print("=== Stepstone Job Scraper (Class-Based) ===\n")
        
        scraper = StepstoneScraper()
        result = await scraper.scrape(test_url)
        
        if result:
            print("\n=== Final Extracted Data ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            save_to_json(result, 'data/job_data.json')
            print("\n✓ Saved to data/job_data.json")
        else:
            print("\n✗ Scraping failed!")
    
    asyncio.run(main())
