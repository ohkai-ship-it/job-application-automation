import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Union
try:
    from .utils.logging import get_logger
    from .utils.http import request_with_retries
    from .utils.errors import ScraperError
except Exception:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.logging import get_logger
    from utils.http import request_with_retries
    from utils.errors import ScraperError

# Type aliases for clarity
JobData = Dict[str, Any]
Address = Dict[str, str]
JsonLD = Dict[str, Any]

def clean_job_title(title: Optional[str]) -> Optional[str]:
    """
    Remove gender markers from job titles
    
    Args:
        title: Original job title
        
    Returns:
        Cleaned job title or None if input was None
    """
    if not title:
        return title
    
    # Common gender markers to remove
    gender_patterns: List[str] = [
        r'\(m/w/d\)', r'\(w/m/d\)', r'\(d/m/w\)',
        r'\(m/f/d\)', r'\(f/m/d\)', r'\(gn\)',
        r'\(m/w\)', r'\(w/m\)',
        r'\(all genders\)', r'\(x/w/m\)',
        r'm/w/d', r'w/m/d',
    ]
    
    cleaned = title
    for pattern in gender_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces and dashes
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s*-\s*$', '', cleaned)
    cleaned = re.sub(r'^\s*-\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


def scrape_stepstone_job(url: str) -> Optional[JobData]:
    """
    Scrape job posting data from Stepstone
    
    Args:
        url: URL of the Stepstone job posting
        
    Returns:
        Dictionary containing job data or None if scraping failed
    """



def split_address(address_dict: Address) -> Tuple[str, str]:
    """
    Split address into two lines for letter formatting
    
    Args:
        address_dict: Address dictionary containing street, postal code, city
        
    Returns:
        Tuple of (line1, line2) where line1 is street and line2 is postal code + city
    """
    line1 = address_dict.get('streetAddress', '')
    
    # Build line 2: postal code + city
    parts = []
    if address_dict.get('postalCode'):
        parts.append(address_dict['postalCode'])
    if address_dict.get('addressLocality'):
        parts.append(address_dict['addressLocality'])
    
    line2 = ' '.join(parts)
    
    return (line1, line2)


def scrape_stepstone_job(url: str) -> Optional[JobData]:
    """
    Scrapes a Stepstone job posting and extracts key information.
    
    Args:
        url: The URL of the Stepstone job posting
        
    Returns:
        Dictionary containing extracted job information or None if scraping failed
    """
    
    # Initialize result dictionary
    job_data = {
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
        'direct_apply_link': None,  # Direct application link on company site
        'publication_date': None,
        'job_description': None,
        'contact_person': {
            'name': None,
            'email': None,
            'phone': None
        },
        'scraped_at': datetime.now().isoformat(),
        'source_url': url
    }
    
    logger = get_logger(__name__)

    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        # Fetch the page with retries
        logger.info("Fetching URL: %s", url)
        try:
            response = request_with_retries('GET', url, headers=headers, timeout=10)
        except requests.HTTPError as e:
            status = getattr(getattr(e, 'response', None), 'status_code', 'unknown')
            text = getattr(getattr(e, 'response', None), 'text', '')
            logger.error("HTTP error fetching %s (status %s): %s", url, status, str(e))
            raise ScraperError(f"HTTP {status} for {url}") from e
        except requests.RequestException as e:
            logger.error("Network error fetching %s: %s", url, e)
            raise ScraperError(f"Network error for {url}") from e

        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')

        logger.debug("Page fetched successfully. Extracting data...")
        
        # Extract Stepstone Job ID from URL
        # URL format: ...--JobTitle--JOBID-inline.html
        stepstone_id_match = re.search(r'--(\d+)-inline\.html', url)
        if stepstone_id_match:
            job_data['stepstone_job_id'] = stepstone_id_match.group(1)
            logger.debug("Stepstone Job ID: %s", job_data['stepstone_job_id'])
        
        # Extract from JSON-LD (most reliable!)
        json_ld_data = None
        json_ld_script = soup.find('script', type='application/ld+json')
        if json_ld_script and json_ld_script.string:
            try:
                json_ld_data = json.loads(json_ld_script.string)
                logger.debug("Found JSON-LD structured data")
            except:
                pass
        
        # 1. Job Title
        if json_ld_data and 'title' in json_ld_data:
            job_data['job_title'] = json_ld_data['title']
            job_data['job_title_clean'] = clean_job_title(job_data['job_title'])
        else:
            title_tag = soup.find(attrs={'data-at': 'header-job-title'})
            if title_tag:
                job_data['job_title'] = title_tag.get_text(strip=True)
                job_data['job_title_clean'] = clean_job_title(job_data['job_title'])
        
        if job_data['job_title']:
            logger.debug("Job Title: %s", job_data['job_title'])
            if job_data['job_title_clean'] and job_data['job_title'] != job_data['job_title_clean']:
                logger.debug("  Clean: %s", job_data['job_title_clean'])
        
        # 2. Company Name
        if json_ld_data and 'hiringOrganization' in json_ld_data:
            job_data['company_name'] = json_ld_data['hiringOrganization'].get('name')
        else:
            company_tag = soup.find(attrs={'data-at': 'metadata-company-name'})
            if company_tag:
                job_data['company_name'] = company_tag.get_text(strip=True)
        
        if job_data['company_name']:
            logger.debug("Company: %s", job_data['company_name'])
        
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
            logger.debug("Location: %s", job_data['location'])
        
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
            logger.debug("Work Mode: %s", job_data['work_mode'])
        
        # 5. Publication Date
        if json_ld_data and 'datePosted' in json_ld_data:
            job_data['publication_date'] = json_ld_data['datePosted']
            logger.debug("Publication Date: %s", job_data['publication_date'])
        
        # 6. Job Description
        if json_ld_data and 'description' in json_ld_data:
            desc_html = json_ld_data['description']
            desc_soup = BeautifulSoup(desc_html, 'lxml')
            job_data['job_description'] = desc_soup.get_text(separator='\n', strip=True)
            desc_preview = job_data['job_description'][:200] + "..."
            logger.debug("Job Description preview: %s", desc_preview)
        
        # 6b. Extract Company Reference Number from job description
        # Look for common patterns: "Referenznummer:", "Job-ID:", "Kennziffer:", etc.
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
                    logger.debug("Company Reference Number: %s", job_data['company_job_reference'])
                    break
        
        # Also check if it's in JSON-LD
        if json_ld_data and 'identifier' in json_ld_data:
            if not job_data['company_job_reference']:
                ref_value = json_ld_data['identifier']
                if isinstance(ref_value, dict):
                    ref_value = ref_value.get('value', '')
                job_data['company_job_reference'] = str(ref_value)
                logger.debug("Company Reference (from JSON-LD): %s", job_data['company_job_reference'])
        
        # 7. Company Address
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
                    # Split into two lines
                    lines = split_address(address)
                    job_data['company_address_line1'] = lines[0]
                    job_data['company_address_line2'] = lines[1]
                    logger.debug("Company Address: %s", job_data['company_address'])
                    logger.debug("  Line 1: %s", job_data['company_address_line1'])
                    logger.debug("  Line 2: %s", job_data['company_address_line2'])
        
        # 8. Website Link
        real_company_website = None
        
        if json_ld_data and 'hiringOrganization' in json_ld_data:
            org = json_ld_data['hiringOrganization']
            if 'url' in org:
                url_value = org['url']
                if 'stepstone.de' not in url_value:
                    real_company_website = url_value
                    job_data['website_link'] = url_value
                    logger.debug("Company Website: %s", job_data['website_link'])
        
        # Construct likely company website from company name
        if not real_company_website and job_data.get('company_name'):
            company_clean = job_data['company_name'].lower()
            # Remove common company suffixes
            for suffix in ['gmbh', 'ag', 'se', 'kg', 'ohg', 'gbr', 'ug', 'ev', 'mbh', 'ltd', 'inc', 'llc', 'corp']:
                company_clean = company_clean.replace(' ' + suffix, '')
            # Remove non-alphanumeric characters
            company_clean = re.sub(r'[^a-z0-9]', '', company_clean)
            
            job_data['website_link'] = f"https://www.{company_clean}.de"
            logger.debug("Estimated Website: %s", job_data['website_link'])
            real_company_website = job_data['website_link']
        
        # 9. Career Page Link - only set if we have a valid website
        if real_company_website and real_company_website.startswith('http'):
            if 'stepstone.de' not in real_company_website:
                base_url = real_company_website.rstrip('/')
                job_data['career_page_link'] = f"{base_url}/karriere"
                logger.debug("Career Page (estimated): %s", job_data['career_page_link'])
                
        # 10. Direct Apply Link - look for "Jetzt bewerben" or "Apply now" buttons
        apply_buttons = soup.find_all(['a', 'button'], string=re.compile('jetzt bewerben|apply now|bewerben', re.I))
        for button in apply_buttons:
            if button.name == 'a' and button.get('href'):
                href = button['href']
                # Skip if it's just a Stepstone internal link
                if 'stepstone.de' not in href or '/go/' in href:
                    job_data['direct_apply_link'] = href if href.startswith('http') else f'https://{href}'
                    logger.debug("Direct Apply Link: %s", job_data['direct_apply_link'])
                    break
        
        # 11. Contact Information
        page_text = soup.get_text()
        
        # Email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
        emails = [e for e in emails if not any(x in e.lower() for x in ['beispiel', 'example', 'noreply'])]
        if emails:
            job_data['contact_person']['email'] = emails[0]
            logger.debug("Contact Email: %s", job_data['contact_person']['email'])
        
        # Phone
        phones = re.findall(r'\+?\d{2,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}', page_text)
        phones = [p for p in phones if len(p.replace(' ', '').replace('-', '')) > 8]
        if phones:
            job_data['contact_person']['phone'] = phones[0].strip()
            logger.debug("Contact Phone: %s", job_data['contact_person']['phone'])
        
        logger.info("Scraping completed successfully")
        return job_data

    except ScraperError:
        # Already logged above
        return None
    except Exception as e:
        from traceback import format_exc
        logger.exception("Error parsing page %s: %s", url, e)
        logger.debug("Traceback: %s", format_exc())
        return None


def save_to_json(data: JobData, filename: Union[str, Path]) -> None:
    """
    Save scraped data to JSON file
    
    Args:
        data: Job data dictionary to save
        filename: Path to the output JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Test function
if __name__ == "__main__":
    test_url = "https://www.stepstone.de/stellenangebote--Program-Manager-Aachen-Duesseldorf-bundesweit-Utimaco-GmbH--12311219-inline.html"
    print("=== Stepstone Job Scraper ===\n")
    
    result = scrape_stepstone_job(test_url)
    
    if result:
        print("\n=== Final Extracted Data ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        save_to_json(result, 'data/job_data.json')
    else:
        print("\n✗ Scraping failed!")