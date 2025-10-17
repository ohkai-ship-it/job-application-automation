"""
LinkedIn Job Scraper using Playwright for dynamic content

Extracts full job descriptions from LinkedIn by rendering the page
with JavaScript execution (required for dynamic content loading).
"""

import asyncio
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def extract_job_id_from_url(url: str) -> str:
    """Extract job ID from LinkedIn URL"""
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


async def extract_job_description_playwright(url: str) -> Optional[str]:
    """
    Extract full job description using Playwright to render JavaScript.
    
    This is necessary because LinkedIn loads job content dynamically.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate to the job page with reasonable timeout
            try:
                await page.goto(url, wait_until='load', timeout=20000)
            except:
                # If timeout, continue anyway - content might still be there
                pass
            
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(2000)
            
            # Wait for job description to load (multiple selectors to try)
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
                # Clean up excessive whitespace
                text = re.sub(r'\s+', ' ', text)
                return text
            
            return None
            
    except Exception as e:
        print(f"Playwright extraction failed: {e}")
        return None


def extract_job_description(soup) -> str:
    """Fallback: Try to extract job description from static HTML"""
    
    # Try different selectors for job description
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
            if text and len(text) > 100:  # Only if substantial content
                return text[:1000] + "..." if len(text) > 1000 else text
    
    # Fallback: look for any substantial text content
    all_text = soup.get_text()
    if 'beschreibung' in all_text.lower() or 'description' in all_text.lower():
        # Try to find text after "description" keyword
        lines = all_text.split('\n')
        desc_found = False
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if desc_found and line and len(line) > 20:
                description_lines.append(line)
                if len('\n'.join(description_lines)) > 500:
                    break
            elif any(word in line.lower() for word in ['beschreibung', 'description', 'aufgaben', 'responsibilities']):
                desc_found = True
                if len(line) > 20:  # If the description starts on same line
                    description_lines.append(line)
        
        if description_lines:
            result = '\n'.join(description_lines)
            return result[:1000] + "..." if len(result) > 1000 else result
    
    return '[Job description not accessible without login]'


def format_linkedin_description(description: str) -> str:
    """
    Format LinkedIn job description for better readability in Trello.
    Breaks long blocks into sections with line breaks.
    
    Args:
        description: Raw job description text from Playwright
        
    Returns:
        Formatted description with section breaks
    """
    if not description:
        return description
    
    # Clean up excessive whitespace
    text = re.sub(r'\s+', ' ', description).strip()
    
    # Remove leading "Description" or "Summary of This Role" etc
    text = re.sub(r'^(Description|Summary|About the role|The role|This position)\s*', '', text, flags=re.IGNORECASE)
    
    # Remove emojis
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text).strip()
    
    # Split into sentences for better formatting
    # Look for common section headers and add line breaks
    section_headers = [
        'What Part Will You Play',
        'What Are We Looking For',
        'Minimum Qualifications',
        'Core Competencies',
        'Essential Knowledge',
        'Key Skills',
        'Required Abilities',
        'Expected Behaviors',
        'What We Offer',
        'Responsibilities',
        'Requirements',
        'Qualifications',
        'Benefits',
        'About Us',
        'Your Profile',
        'Your Background',
        'We Are Looking For',
        'You Have',
    ]
    
    # Add line breaks before section headers
    formatted = text
    for header in section_headers:
        # Match with optional punctuation and case insensitive
        pattern = rf'(\s)({header}\??)'
        formatted = re.sub(pattern, r'\n\n\2', formatted, flags=re.IGNORECASE)
    
    # Add line breaks at natural sentence boundaries (periods followed by capital letters)
    # But only if they would make lines reasonably sized
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', formatted)
    
    # Group sentences into logical chunks (roughly paragraph-sized)
    result_paragraphs = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # If adding this sentence would make paragraph too long, start new one
        if current_length + len(sentence) > 200 and current_chunk:
            result_paragraphs.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence) + 1
    
    if current_chunk:
        result_paragraphs.append(' '.join(current_chunk))
    
    # Join paragraphs with double line breaks for readability
    result = '\n\n'.join(result_paragraphs)
    
    # Clean up any multiple line breaks
    result = re.sub(r'\n\n+', '\n\n', result)
    
    return result.strip()


def scrape_linkedin_job(url: str) -> dict:
    """
    Simple LinkedIn job scraper
    
    Returns job_data dict compatible with existing workflow
    """
    print(f"Scraping LinkedIn job: {url}")
    
    # Extract job ID
    job_id = extract_job_id_from_url(url)
    if not job_id:
        print("Could not extract job ID")
        return None
    
    # Convert to direct job view URL
    direct_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    
    # Make request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(direct_url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract from page title
        title = soup.find('title')
        if not title:
            return None
        
        title_text = title.get_text().strip().replace(' | LinkedIn', '')
        
        # Parse title: "Company hiring Job Title in Location"
        company_name = "Unknown Company"
        job_title = title_text
        location = "Unknown Location"
        company_portal = None  # Company website/portal link
        company_address = "Not available"  # Will try to extract from description
        
        if ' hiring ' in title_text and ' in ' in title_text:
            match = re.search(r'(.+?)\s+hiring\s+(.+?)\s+in\s+(.+?)$', title_text)
            if match:
                company_name = match.group(1).strip()
                job_title = match.group(2).strip() 
                location = match.group(3).strip()
        
        # Clean up emojis
        company_name = re.sub(r'[\U0001F300-\U0001F9FF]', '', company_name).strip()
        job_title = re.sub(r'[\U0001F300-\U0001F9FF]', '', job_title).strip()
        
        # Try to extract job description using Playwright first (for full content)
        job_description = None
        if PLAYWRIGHT_AVAILABLE:
            try:
                job_description = asyncio.run(extract_job_description_playwright(direct_url))
            except Exception as e:
                print(f"Playwright failed, falling back to static parsing: {e}")
        
        # Fallback to static HTML parsing if Playwright not available or failed
        if not job_description:
            job_description = extract_job_description(soup)
        
        # Format the description for better readability
        if job_description and job_description != '[Job description not accessible without login]':
            job_description = format_linkedin_description(job_description)
        
        # Try to extract company website/portal link
        # Look for links in the company section (usually first few links)
        company_portal = None
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            # Skip LinkedIn internal links
            if 'linkedin.com' in href:
                continue
            
            # Look for company website indicators
            if any(keyword in link_text for keyword in ['company website', 'visit company', 'careers', 'jobs', 'company page', 'learn more']):
                company_portal = href
                break
            
            # Also check if it's an external link early in the page
            if company_portal is None and 'linkedin' not in href and 'https://' in href and len(company_portal or '') == 0:
                # Could be a company link
                if not any(word in href for word in ['tracking', 'redirect']):
                    company_portal = href
        
        # If we couldn't find a portal link, generate a crude one (like Stepstone does)
        if not company_portal:
            # Use Stepstone's crude approach: extract domain from company name and add /karriere
            company_clean = re.sub(r'[^a-z0-9\s]', '', company_name.lower())
            company_clean = '-'.join(company_clean.split())  # Replace spaces with hyphens
            # Remove non-alphanumeric except hyphens
            company_clean = re.sub(r'[^a-z0-9-]', '', company_clean)
            
            if company_clean:
                company_portal = f"https://www.{company_clean}.de/karriere"
        
        # Try to extract company address from description
        # Look for patterns like "Address:", "Location:", "Based in", etc.
        if job_description:
            address_patterns = [
                r'(?:Address|Headquarters|Located):\s*(.+?)(?:\n|,)',
                r'(?:Based in|Office in):\s*(.+?)(?:\n|,)',
                r'(\d+\s+\w+(?:\s+\w+)?,\s+\d{5},?\s+\w+)',  # Street address pattern
            ]
            for pattern in address_patterns:
                match = re.search(pattern, job_description, re.IGNORECASE)
                if match:
                    company_address = match.group(1).strip()
                    break
        
        # Return in standard format
        return {
            'company_name': company_name,
            'job_title': job_title,
            'job_description': job_description,
            'location': location,
            'source_url': url,
            'company_address': company_address,
            'career_page_link': company_portal,  # Use same field name as Stepstone scraper
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_linkedin_scraper():
    """Test with the provided URL"""
    test_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253399100"
    
    job_data = scrape_linkedin_job(test_url)
    if job_data:
        print("SUCCESS!")
        print("="*80)
        for key, value in job_data.items():
            print(f"{key.upper()}:")
            if key == 'job_description' and len(str(value)) > 100:
                # Print description with better formatting
                desc = str(value)
                words = desc.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    if len(' '.join(current_line)) > 80:
                        lines.append(' '.join(current_line[:-1]))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                for line in lines:
                    print(f"  {line}")
            else:
                print(f"  {value}")
            print()
    else:
        print("Failed")


if __name__ == "__main__":
    test_linkedin_scraper()