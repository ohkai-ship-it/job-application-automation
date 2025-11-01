"""
LinkedIn Job Scraper - Class-Based Architecture
Extracts full job descriptions from LinkedIn using Playwright for dynamic content.
"""

import asyncio
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from .scraper import BaseJobScraper, JobData
    from .utils.log_config import get_logger
except Exception:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from scraper import BaseJobScraper, JobData
    from utils.log_config import get_logger


class LinkedInScraper(BaseJobScraper):
    """
    Scraper for LinkedIn job postings.
    Uses Playwright to render JavaScript and extract dynamic content.
    Falls back to static HTML parsing if Playwright is unavailable.
    """
    
    async def scrape(self, url: str) -> Optional[JobData]:
        """Scrape a LinkedIn job posting."""
        job_data = self._create_empty_job_data(url)
        
        try:
            self.logger.info("Scraping LinkedIn job: %s", url)
            
            job_id = self._extract_job_id(url)
            if not job_id:
                self.logger.error("Could not extract job ID from URL: %s", url)
                return None
            
            job_data['linkedin_job_id'] = job_id
            direct_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            try:
                response = requests.get(direct_url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                self.logger.error("Network error fetching LinkedIn URL: %s", e)
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_text = self._extract_title_text(soup)
            if not title_text:
                self.logger.error("Could not extract title from page")
                return None
            
            parsed = self._parse_title_text(title_text)
            job_data['company_name'] = parsed['company_name']
            job_data['job_title'] = parsed['job_title']
            job_data['location'] = parsed['location']
            
            self.logger.debug("Company: %s", job_data['company_name'])
            self.logger.debug("Job Title: %s", job_data['job_title'])
            self.logger.debug("Location: %s", job_data['location'])
            
            job_description = None
            if PLAYWRIGHT_AVAILABLE:
                try:
                    job_description, publication_date, work_mode = await self._scrape_with_playwright(direct_url)
                    job_data['publication_date'] = publication_date
                    job_data['work_mode'] = work_mode
                    self.logger.debug("Successfully extracted description with Playwright")
                except Exception as e:
                    self.logger.warning("Playwright failed, falling back: %s", e)
            
            if not job_description:
                job_description = self._extract_from_static_html(soup)
                self.logger.debug("Extracted description from static HTML")
            
            if job_description and '[Job description not accessible' not in job_description:
                job_description = self._format_description(job_description)
            
            job_data['job_description'] = job_description
            
            # Extract work mode from job posting (if not already extracted by Playwright)
            if not job_data.get('work_mode'):
                job_data['work_mode'] = self._extract_work_mode(soup)
            
            if job_data.get('work_mode'):
                self.logger.debug("Work Mode: %s", job_data['work_mode'])
            
            # Publication date already extracted from Playwright above (if available)
            if not job_data.get('publication_date'):
                job_data['publication_date'] = self._extract_publication_date_from_soup(soup)
            
            if job_data.get('publication_date'):
                self.logger.debug("Publication Date: %s", job_data['publication_date'])
            
            # Extract industry from sidebar criteria
            industry = self._extract_industry_from_soup(soup)
            if industry:
                job_data['industry'] = industry
                self.logger.debug("Industry: %s", job_data['industry'])
            
            # Extract company address from description
            # Pass location as fallback (e.g., "Düsseldorf")
            if job_data['job_description']:
                job_data['company_address'] = self._extract_address(
                    job_data['job_description'],
                    fallback_location=job_data.get('location')
                )
                if job_data['company_address']:
                    self.logger.debug("Company Address: %s", job_data['company_address'])
                    self.logger.info("  Address: %s", job_data['company_address'])
            
            job_data['scraped_at'] = datetime.now().isoformat()
            
            self.logger.info("Scraping completed successfully")
            return job_data
            
        except Exception as e:
            self.logger.exception("Error scraping LinkedIn job: %s", e)
            return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL."""
        if 'currentJobId=' in url:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return params.get('currentJobId', [None])[0]
        elif '/jobs/view/' in url:
            match = re.search(r'/jobs/view/(\d+)', url)
            return match.group(1) if match else None
        else:
            match = re.search(r'(\d{10,})', url)
            return match.group(1) if match else None
    
    def _extract_title_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title text from page."""
        title = soup.find('title')
        if title:
            text = title.get_text().strip()
            return text.replace(' | LinkedIn', '')
        return None
    
    def _parse_title_text(self, title_text: str) -> Dict[str, str]:
        """Parse title text into components."""
        company_name = "Unknown Company"
        job_title = title_text
        location = "Unknown Location"
        
        if ' hiring ' in title_text and ' in ' in title_text:
            match = re.search(r'(.+?)\s+hiring\s+(.+?)\s+in\s+(.+?)$', title_text)
            if match:
                company_name = match.group(1).strip()
                job_title = match.group(2).strip()
                location = match.group(3).strip()
        
        company_name = re.sub(r'[\U0001F300-\U0001F9FF]', '', company_name).strip()
        job_title = re.sub(r'[\U0001F300-\U0001F9FF]', '', job_title).strip()
        
        return {
            'company_name': company_name,
            'job_title': job_title,
            'location': location
        }
    
    async def _scrape_with_playwright(self, url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract full job description, publication date, and work mode using Playwright.
        Returns tuple: (description, publication_date, work_mode)
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                try:
                    await page.goto(url, wait_until='load', timeout=20000)
                except:
                    pass
                
                await page.wait_for_timeout(2000)
                
                # Extract description
                selectors = [
                    '[data-test-id="job-description"]',
                    'div.show-more-less-html__markup',
                    '.jobs-details__main-content',
                    'section.description',
                ]
                
                description = None
                for selector in selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible():
                            description = await element.text_content()
                            if description and len(description.strip()) > 100:
                                break
                    except:
                        pass
                
                # Extract full page HTML for date and work mode
                page_html = await page.content()
                publication_date = self._extract_date_from_html(page_html)
                work_mode = self._extract_work_mode_from_html(page_html)
                
                await context.close()
                await browser.close()
                
                if description:
                    text = description.strip()
                    text = re.sub(r'\s+', ' ', text)
                else:
                    text = None
                
                return text, publication_date, work_mode
                
        except Exception as e:
            self.logger.debug("Playwright extraction failed: %s", e)
            return None, None, None
    
    def _extract_from_static_html(self, soup: BeautifulSoup) -> str:
        """Fallback: Extract job description from static HTML."""
        selectors = [
            'div[data-automation-id="jobDescription"]',
            '.jobs-description__content',
            '.jobs-box__content',
            '.description__text',
            'div.jobs-description-content__text',
            '[data-test-id="job-description"]',
            '.jobs-description',
            'section.jobs-section',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 100:
                    return text[:1000] + "..." if len(text) > 1000 else text
        
        return '[Job description not accessible without login]'
    
    def _format_description(self, description: str) -> str:
        """Format job description for better readability."""
        if not description:
            return description
        
        text = re.sub(r'\s+', ' ', description).strip()
        text = re.sub(r'^(Description|Summary|About the role)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text).strip()
        
        section_headers = [
            'What Part Will You Play',
            'What Are We Looking For',
            'Responsibilities',
            'Requirements',
            'Qualifications',
            'Benefits',
        ]
        
        formatted = text
        for header in section_headers:
            pattern = rf'(\s)({header}\??)'
            formatted = re.sub(pattern, r'\n\n\2', formatted, flags=re.IGNORECASE)
        
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', formatted)
        result_paragraphs = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) > 200 and current_chunk:
                result_paragraphs.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = len(sentence)
            else:
                current_chunk.append(sentence)
                current_length += len(sentence) + 1
        
        if current_chunk:
            result_paragraphs.append(' '.join(current_chunk))
        
        result = '\n\n'.join(result_paragraphs)
        result = re.sub(r'\n\n+', '\n\n', result)
        
        return result.strip()
    
    def _extract_work_mode_from_html(self, html_content: str) -> Optional[str]:
        """
        Extract work mode from rendered HTML content.
        LinkedIn shows work mode as badge/chip buttons under the job title.
        They appear as clickable elements with checkmarks: ✓ Hybrid, ✓ Remote, etc.
        
        Returns: 'remote', 'hybrid', or 'onsite'
        """
        try:
            html_lower = html_content.lower()
            
            # Strategy: LinkedIn shows work mode in badge buttons under the job title
            # Look for patterns like: <button>✓ Hybrid</button> or similar markup
            
            # Try to extract just the job header/title section which contains the work mode badges
            # This avoids false positives from tracking attributes
            header_match = re.search(
                r'<[^>]*class="[^"]*jobs-details[^"]*"[^>]*>(.*?)<[^>]*class="[^"]*description[^"]*"',
                html_content,
                re.IGNORECASE | re.DOTALL
            )
            
            if header_match:
                search_text = header_match.group(1).lower()
                self.logger.debug("Searching in extracted header section (%d chars)", len(search_text))
            else:
                search_text = html_lower
                self.logger.debug("Using full HTML for search")
            
            # Look for work mode text in button/span elements (with or without checkmark)
            # Pattern: ">  Hybrid  <" or "> ✓ Hybrid <" etc
            
            # Check for hybrid FIRST (most specific - must come before on-site check)
            if re.search(r'>\s*[✓✔]?\s*hybrid\s*<', search_text) or \
               re.search(r'\bhybrid\b', search_text):
                self.logger.info("✓ Work mode detected: HYBRID")
                return 'hybrid'
            
            # Check for remote
            if re.search(r'>\s*[✓✔]?\s*remote\s*<', search_text) or \
               re.search(r'\b(?:remote|work\s*from\s*home)\b', search_text):
                self.logger.info("✓ Work mode detected: REMOTE")
                return 'remote'
            
            # Check for on-site (check this LAST to avoid false positives)
            if re.search(r'>\s*[✓✔]?\s*(?:on-site|onsite)\s*<', search_text) or \
               re.search(r'\b(?:on-site|onsite|office\s*based)\b', search_text):
                self.logger.info("✓ Work mode detected: ON-SITE")
                return 'onsite'
            
            self.logger.warning("⚠ No work mode pattern found")
            return None
            
        except Exception as e:
            self.logger.error("✗ Error extracting work mode from HTML: %s", e)
            return None
    
    def _extract_work_mode(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract work mode (remote, hybrid, onsite) from LinkedIn page.
        First tries job criteria section, then falls back to job description text.
        Uses priority hierarchy: remote > hybrid > on-site
        If not found in either, returns None (no label will be set).
        """
        try:
            found_modes = set()
            
            # Strategy 1: Look in job criteria section (if visible)
            criteria_sections = soup.find_all('li', class_=re.compile(r'description__job-criteria-item'))
            
            for section in criteria_sections:
                text = section.get_text(strip=True).lower()
                
                # Check for all patterns, collect all matches
                if re.search(r'\bhybrid\b', text):
                    found_modes.add('hybrid')
                    self.logger.debug("Found 'hybrid' in criteria section")
                
                if re.search(r'\b(?:remote|work\s+from\s+home|wfh)\b', text):
                    found_modes.add('remote')
                    self.logger.debug("Found 'remote' in criteria section")
                
                if re.search(r'\b(?:on-site|onsite|on\s+site|office)\b', text):
                    found_modes.add('onsite')
                    self.logger.debug("Found 'on-site' in criteria section")
            
            # If found in criteria, use the highest priority
            if found_modes:
                return self._get_highest_priority_mode(found_modes)
            
            # Strategy 2: Fallback - search in job description text
            desc_text = soup.get_text(separator=' ').lower()
            
            if desc_text:
                # Check for all patterns, collect all matches
                if re.search(r'\bhybrid\b', desc_text):
                    found_modes.add('hybrid')
                    self.logger.debug("Found 'hybrid' in job description")
                
                if re.search(r'\b(?:remote|work\s+from\s+home|homeoffice|home\s+office|wfh)\b', desc_text):
                    found_modes.add('remote')
                    self.logger.debug("Found 'remote' in job description")
                
                if re.search(r'\b(?:on-site|onsite|on\s+site|office)\b', desc_text):
                    found_modes.add('onsite')
                    self.logger.debug("Found 'on-site' in job description")
            
            if found_modes:
                return self._get_highest_priority_mode(found_modes)
            
            self.logger.debug("No work mode pattern found - leaving unset")
            return None
            
        except Exception as e:
            self.logger.error("Error extracting work mode: %s", e)
            return None
    
    def _get_highest_priority_mode(self, modes: set) -> str:
        """
        Return the highest priority work mode.
        Priority hierarchy: remote > hybrid > on-site
        """
        if 'remote' in modes:
            self.logger.debug("Multiple modes found, using highest priority: remote")
            return 'remote'
        elif 'hybrid' in modes:
            self.logger.debug("Multiple modes found, using highest priority: hybrid")
            return 'hybrid'
        elif 'onsite' in modes:
            self.logger.debug("Using mode: on-site")
            return 'onsite'
        return None
    
    def _extract_date_from_html(self, html: str) -> Optional[str]:
        """
        Extract publication date from rendered HTML content (from Playwright).
        Searches for "Posted X days ago", "Reposted X days ago", or similar patterns.
        Returns ISO 8601 format date.
        """
        try:
            from datetime import datetime, timedelta
            
            # Search for date text in HTML
            date_patterns = [
                r'(?:Posted|Reposted)\s+(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago',
                r'Updated\s+(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago',
                r'(\d{4}-\d{2}-\d{2})',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        # Relative date format
                        number = int(match.group(1))
                        unit = match.group(2).lower().rstrip('s')
                        
                        now = datetime.utcnow()
                        
                        if unit == 'second':
                            pub_date = now - timedelta(seconds=number)
                        elif unit == 'minute':
                            pub_date = now - timedelta(minutes=number)
                        elif unit == 'hour':
                            pub_date = now - timedelta(hours=number)
                        elif unit == 'day':
                            pub_date = now - timedelta(days=number)
                        elif unit == 'week':
                            pub_date = now - timedelta(weeks=number)
                        elif unit == 'month':
                            pub_date = now - timedelta(days=number * 30)
                        else:
                            continue
                        
                        self.logger.debug("Publication date extracted: %s", pub_date.isoformat())
                        return pub_date.isoformat() + 'Z'
                    else:
                        # ISO format date
                        date_str = match.group(1)
                        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                            self.logger.debug("Publication date extracted: %s", date_str)
                            return f"{date_str}T00:00:00Z"
            
            self.logger.debug("No publication date found in HTML")
            return None
        except Exception as e:
            self.logger.debug("Error extracting date from HTML: %s", e)
            return None

    def _extract_publication_date_from_soup(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract job publication date from static soup content.
        Returns ISO 8601 format date.
        Fallback when Playwright is not available.
        """
        try:
            from datetime import datetime, timedelta
            
            # Try to find posted/updated date in the page
            date_patterns = [
                r'(?:Posted|Reposted)\s+(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago',
                r'Updated\s+(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago',
                r'(\d{4}-\d{2}-\d{2})',
            ]
            
            # Search in visible text
            page_text = soup.get_text()
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        # Relative date format
                        number = int(match.group(1))
                        unit = match.group(2).lower().rstrip('s')
                        
                        now = datetime.utcnow()
                        
                        if unit == 'second':
                            pub_date = now - timedelta(seconds=number)
                        elif unit == 'minute':
                            pub_date = now - timedelta(minutes=number)
                        elif unit == 'hour':
                            pub_date = now - timedelta(hours=number)
                        elif unit == 'day':
                            pub_date = now - timedelta(days=number)
                        elif unit == 'week':
                            pub_date = now - timedelta(weeks=number)
                        elif unit == 'month':
                            pub_date = now - timedelta(days=number * 30)
                        else:
                            continue
                        
                        return pub_date.isoformat() + 'Z'
                    else:
                        # ISO format date
                        date_str = match.group(1)
                        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                            return f"{date_str}T00:00:00Z"
            
            return None
        except Exception as e:
            self.logger.debug("Error extracting publication date from soup: %s", e)
            return None
    
    def _extract_industry_from_soup(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract industry information from LinkedIn sidebar criteria.
        Looks for elements with class 'description__job-criteria-item' that contain 'Industries'.
        Returns comma-separated string of industries, or None if not found.
        """
        try:
            # Find all job criteria items
            criteria_items = soup.find_all(class_=lambda x: x and 'description__job-criteria-item' in (x if x else ''))
            
            for item in criteria_items:
                text = item.get_text(separator=' | ', strip=True)
                parts = text.split(' | ')
                
                # Look for the "Industries" label (case-insensitive)
                if len(parts) >= 2 and parts[0].strip().lower() == 'industries':
                    industry_value = ' | '.join(parts[1:]).strip()
                    self.logger.debug("Industry extracted from sidebar: %s", industry_value)
                    return industry_value
            
            self.logger.debug("No industry information found in sidebar criteria")
            return None
            
        except Exception as e:
            self.logger.debug("Error extracting industry from sidebar: %s", e)
            return None
    
    def _extract_company_portal(self, soup: BeautifulSoup, company_name: str) -> Optional[str]:
        """Extract company website/portal link."""
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            if 'linkedin.com' in href:
                continue
            
            if any(keyword in link_text for keyword in ['company website', 'careers', 'jobs']):
                return href
        
        company_clean = re.sub(r'[^a-z0-9\s]', '', company_name.lower())
        company_clean = '-'.join(company_clean.split())
        company_clean = re.sub(r'[^a-z0-9-]', '', company_clean)
        
        if company_clean:
            return f"https://www.{company_clean}.de/karriere"
        
        return None
    
    def _extract_address(self, description: str, fallback_location: Optional[str] = None) -> Optional[str]:
        """
        Extract company address from description text.
        
        Strategy:
        1. Search description for address keywords (Address, Headquarters, Based in, Office in, etc.)
        2. If found, return the address
        3. If not found in description, return None (NOT the fallback location)
        
        The fallback_location is only passed for reference but is not used as a fallback.
        This ensures we only set company_address when explicitly found in the description.
        
        Args:
            description: Job description text
            fallback_location: Card location (e.g., "Düsseldorf") - reference only, not used as fallback
            
        Returns:
            Address string if found in description, else None
        """
        if not description:
            return None
        
        # Search for address keywords in description
        patterns = [
            r'(?:Address|Headquarters|Located):\s*(.+?)(?:\n|,)',
            r'(?:Based in|Office in|Office location):\s*(.+?)(?:\n|,)',
            r'(?:Our office|Our address):\s*(.+?)(?:\n|,)',
            r'(\d+\s+\w+(?:\s+\w+)?,\s+\d{5},?\s+\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                self.logger.debug("Address found in description using pattern: %s", pattern)
                return address
        
        # No address keywords found - return None (not fallback)
        self.logger.debug("No address keywords found in description")
        return None
    
    def _extract_industry_from_html(self, html: str) -> Optional[str]:
        """
        Extract industry information from LinkedIn sidebar criteria.
        Looks for elements with class 'description__job-criteria-item' that contain 'Industries'.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all job criteria items
            criteria_items = soup.find_all(class_=lambda x: x and 'description__job-criteria-item' in (x if x else ''))
            
            for item in criteria_items:
                text = item.get_text(separator=' | ', strip=True)
                parts = text.split(' | ')
                
                # Look for the "Industries" label
                if len(parts) >= 2 and parts[0].strip().lower() == 'industries':
                    industry_value = ' | '.join(parts[1:]).strip()
                    self.logger.debug("Industry extracted: %s", industry_value)
                    return industry_value
            
            self.logger.debug("No industry information found in sidebar criteria")
            return None
            
        except Exception as e:
            self.logger.debug("Error extracting industry from HTML: %s", e)
            return None


if __name__ == "__main__":
    async def main():
        test_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253399100"
        print("=== LinkedIn Job Scraper (Class-Based) ===\n")
        
        scraper = LinkedInScraper()
        result = await scraper.scrape(test_url)
        
        if result:
            print("\n✓ Scraping successful!")
        else:
            print("\n✗ Scraping failed!")
    
    asyncio.run(main())
