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
                    job_description = await self._scrape_with_playwright(direct_url)
                    self.logger.debug("Successfully extracted description with Playwright")
                except Exception as e:
                    self.logger.warning("Playwright failed, falling back: %s", e)
            
            if not job_description:
                job_description = self._extract_from_static_html(soup)
                self.logger.debug("Extracted description from static HTML")
            
            if job_description and '[Job description not accessible' not in job_description:
                job_description = self._format_description(job_description)
            
            job_data['job_description'] = job_description
            job_data['career_page_link'] = self._extract_company_portal(soup, job_data['company_name'])
            
            if job_data['job_description']:
                job_data['company_address'] = self._extract_address(job_data['job_description'])
            
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
    
    async def _scrape_with_playwright(self, url: str) -> Optional[str]:
        """Extract full job description using Playwright."""
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
                
                await context.close()
                await browser.close()
                
                if description:
                    text = description.strip()
                    text = re.sub(r'\s+', ' ', text)
                    return text
                
                return None
                
        except Exception as e:
            self.logger.debug("Playwright extraction failed: %s", e)
            return None
    
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
    
    def _extract_address(self, description: str) -> Optional[str]:
        """Extract company address from description."""
        patterns = [
            r'(?:Address|Headquarters|Located):\s*(.+?)(?:\n|,)',
            r'(?:Based in|Office in):\s*(.+?)(?:\n|,)',
            r'(\d+\s+\w+(?:\s+\w+)?,\s+\d{5},?\s+\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
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
