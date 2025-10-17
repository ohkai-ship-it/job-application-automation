"""
HTML Page Analysis for Job Research.

This module provides utilities to extract structured information from HTML pages,
specifically designed for finding contact persons, company addresses, and job posting details.
"""

import re
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup

try:
    from .log_config import get_logger
    from .http_utils import request_with_retries
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.log_config import get_logger
    from utils.http_utils import request_with_retries


logger = get_logger(__name__)


@dataclass
class ContactPerson:
    """Structured contact person information."""
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class Address:
    """Structured address information."""
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    full_address: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0


class PageAnalyzer:
    """
    Analyzes HTML pages to extract contact information and addresses.
    
    Features:
    - Extract contact persons with titles and emails
    - Find company addresses with German postal code patterns
    - Detect job posting pages
    - Confidence scoring for extracted data
    """
    
    # Regex patterns for extraction
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    # German phone number patterns
    PHONE_PATTERN = re.compile(
        r'(?:\+49|0049|0)\s*(?:\(\d+\)|\d+)[\s\-/]*\d+[\s\-/]*\d+'
    )
    
    # German postal code pattern (5 digits)
    POSTAL_CODE_PATTERN = re.compile(r'\b\d{5}\b')
    
    # Common HR/recruiting job titles (case-insensitive)
    HR_TITLES = [
        "recruiter", "hr manager", "personalreferent", "talent acquisition",
        "recruiting manager", "head of recruiting", "hr business partner",
        "people operations", "human resources", "personalmanager",
        "personalleiter", "recruiting coordinator"
    ]
    
    # Keywords indicating contact sections
    CONTACT_SECTION_KEYWORDS = [
        "contact", "kontakt", "ansprechpartner", "your contact",
        "get in touch", "reach us", "contact person"
    ]
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the PageAnalyzer.
        
        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        logger.info(f"PageAnalyzer initialized | timeout={timeout}s")
    
    def fetch_and_parse(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a URL and parse it with BeautifulSoup.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object or None if fetch failed
        """
        try:
            logger.info(f"Fetching page | url={url}")
            response = request_with_retries(url, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.warning(f"Non-200 status code: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Page parsed successfully | url={url}")
            return soup
            
        except Exception as e:
            logger.error(f"Failed to fetch page: {e}")
            return None
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of unique email addresses
        """
        emails = self.EMAIL_PATTERN.findall(text)
        unique_emails = list(set(emails))
        
        # Filter out common noise emails
        filtered = [
            e for e in unique_emails
            if not any(noise in e.lower() for noise in ['example.com', 'test.com', 'mailto'])
        ]
        
        logger.debug(f"Extracted {len(filtered)} emails from text")
        return filtered
    
    def extract_phones(self, text: str) -> List[str]:
        """
        Extract phone numbers from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of unique phone numbers
        """
        phones = self.PHONE_PATTERN.findall(text)
        unique_phones = list(set(phones))
        
        logger.debug(f"Extracted {len(unique_phones)} phone numbers from text")
        return unique_phones
    
    def extract_contacts(
        self,
        soup: BeautifulSoup,
        prefer_hr: bool = True
    ) -> List[ContactPerson]:
        """
        Extract contact persons from a page.
        
        Args:
            soup: BeautifulSoup object of the page
            prefer_hr: Prioritize HR/recruiting contacts
            
        Returns:
            List of ContactPerson objects, sorted by confidence
        """
        logger.info("Extracting contact persons from page")
        contacts = []
        
        # Strategy 1: Look for contact sections
        contact_sections = []
        for keyword in self.CONTACT_SECTION_KEYWORDS:
            sections = soup.find_all(
                ['div', 'section', 'article'],
                text=re.compile(keyword, re.IGNORECASE)
            )
            contact_sections.extend(sections)
        
        # Also find parent containers of contact keywords
        for keyword in self.CONTACT_SECTION_KEYWORDS:
            for tag in soup.find_all(text=re.compile(keyword, re.IGNORECASE)):
                if tag.parent:
                    contact_sections.append(tag.parent.parent if tag.parent.parent else tag.parent)
        
        # Deduplicate sections
        contact_sections = list(set(contact_sections))
        logger.debug(f"Found {len(contact_sections)} potential contact sections")
        
        # Strategy 2: Extract from contact sections
        for section in contact_sections:
            section_text = section.get_text()
            
            # Look for name patterns (Title Name format)
            # Common German titles: Dr., Prof., Herr, Frau, etc.
            name_pattern = re.compile(
                r'((?:Dr\.|Prof\.|Herr|Frau)\s+)?([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)'
            )
            
            for match in name_pattern.finditer(section_text):
                title_prefix = match.group(1).strip() if match.group(1) else None
                name = match.group(2).strip()
                
                # Look for job title near the name
                job_title = None
                for hr_title in self.HR_TITLES:
                    if re.search(hr_title, section_text, re.IGNORECASE):
                        job_title = hr_title.title()
                        break
                
                # Extract email and phone from same section
                emails = self.extract_emails(section_text)
                phones = self.extract_phones(section_text)
                
                # Calculate confidence
                confidence = 0.5  # Base confidence for being in contact section
                if job_title:
                    confidence += 0.2
                if emails:
                    confidence += 0.2
                if phones:
                    confidence += 0.1
                if prefer_hr and job_title and any(hr in job_title.lower() for hr in ['hr', 'recruit', 'personal']):
                    confidence += 0.2
                
                contacts.append(ContactPerson(
                    name=name,
                    title=job_title,
                    email=emails[0] if emails else None,
                    phone=phones[0] if phones else None,
                    confidence=min(confidence, 1.0)
                ))
        
        # Remove duplicates by name
        unique_contacts = []
        seen_names = set()
        for contact in contacts:
            if contact.name not in seen_names:
                seen_names.add(contact.name)
                unique_contacts.append(contact)
        
        # Sort by confidence
        unique_contacts.sort(key=lambda c: c.confidence, reverse=True)
        
        logger.info(f"Extracted {len(unique_contacts)} unique contacts")
        return unique_contacts
    
    def extract_addresses(
        self,
        soup: BeautifulSoup,
        location_hint: Optional[str] = None
    ) -> List[Address]:
        """
        Extract addresses from a page.
        
        Args:
            soup: BeautifulSoup object of the page
            location_hint: Optional city/location to prioritize (e.g., "Berlin")
            
        Returns:
            List of Address objects, sorted by confidence
        """
        logger.info(f"Extracting addresses | location_hint={location_hint}")
        addresses = []
        
        # Get all text content
        text = soup.get_text()
        
        # Find all postal codes
        postal_matches = self.POSTAL_CODE_PATTERN.finditer(text)
        
        for match in postal_matches:
            postal_code = match.group()
            
            # Get context around postal code (100 chars before and after)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            # Try to extract city name (word after postal code)
            city_match = re.search(rf'{postal_code}\s+([A-ZÄÖÜ][a-zäöüß]+)', context)
            city = city_match.group(1) if city_match else None
            
            # Try to extract street (pattern: Street name + number)
            street_match = re.search(
                r'([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|platz|weg|allee))\s+(\d+[a-z]?)',
                context,
                re.IGNORECASE
            )
            street = street_match.group(0) if street_match else None
            
            # Calculate confidence
            confidence = 0.3  # Base for having postal code
            if city:
                confidence += 0.3
            if street:
                confidence += 0.3
            if location_hint and city and location_hint.lower() in city.lower():
                confidence += 0.2
            
            # Try to construct full address
            address_parts = []
            if street:
                address_parts.append(street)
            if postal_code and city:
                address_parts.append(f"{postal_code} {city}")
            
            full_address = ", ".join(address_parts) if address_parts else None
            
            addresses.append(Address(
                street=street,
                city=city,
                postal_code=postal_code,
                full_address=full_address,
                confidence=min(confidence, 1.0)
            ))
        
        # Remove duplicates
        unique_addresses = []
        seen_addresses = set()
        for addr in addresses:
            key = (addr.postal_code, addr.city)
            if key not in seen_addresses:
                seen_addresses.add(key)
                unique_addresses.append(addr)
        
        # Sort by confidence
        unique_addresses.sort(key=lambda a: a.confidence, reverse=True)
        
        logger.info(f"Extracted {len(unique_addresses)} unique addresses")
        return unique_addresses
    
    def is_job_posting_page(self, soup: BeautifulSoup) -> bool:
        """
        Determine if a page is a job posting.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            True if the page appears to be a job posting
        """
        text = soup.get_text().lower()
        
        # Job posting indicators
        indicators = [
            'job description', 'stellenbeschreibung',
            'responsibilities', 'aufgaben', 'verantwortlichkeiten',
            'requirements', 'anforderungen', 'qualifikationen',
            'apply now', 'jetzt bewerben',
            'benefits', 'we offer', 'wir bieten'
        ]
        
        matches = sum(1 for indicator in indicators if indicator in text)
        
        # If 3+ indicators found, likely a job posting
        is_job_posting = matches >= 3
        
        logger.info(f"Job posting check | matches={matches} | is_job_posting={is_job_posting}")
        return is_job_posting


# Convenience functions
def quick_extract_contacts(url: str) -> List[ContactPerson]:
    """
    Quick utility to extract contacts from a URL.
    
    Args:
        url: URL to analyze
        
    Returns:
        List of ContactPerson objects
    """
    analyzer = PageAnalyzer()
    soup = analyzer.fetch_and_parse(url)
    if soup:
        return analyzer.extract_contacts(soup)
    return []


def quick_extract_addresses(url: str, location_hint: Optional[str] = None) -> List[Address]:
    """
    Quick utility to extract addresses from a URL.
    
    Args:
        url: URL to analyze
        location_hint: Optional city to prioritize
        
    Returns:
        List of Address objects
    """
    analyzer = PageAnalyzer()
    soup = analyzer.fetch_and_parse(url)
    if soup:
        return analyzer.extract_addresses(soup, location_hint)
    return []


# Module-level test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    
    import logging as stdlib_logging
    stdlib_logging.basicConfig(
        level=stdlib_logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    print("=" * 80)
    print("PAGE ANALYZER MODULE TEST")
    print("=" * 80)
    
    # Test with a sample HTML
    sample_html = """
    <html>
    <body>
        <section class="contact">
            <h2>Kontakt</h2>
            <p>Ihr Ansprechpartner:</p>
            <p>Dr. Michael Schmidt<br>
            Head of Recruiting<br>
            Email: michael.schmidt@example-company.de<br>
            Tel: +49 30 1234567</p>
        </section>
        <div class="address">
            <h3>Unsere Adresse</h3>
            <p>Example GmbH<br>
            Musterstraße 123<br>
            10115 Berlin<br>
            Deutschland</p>
        </div>
        <div class="job-content">
            <h1>Software Engineer Position</h1>
            <h2>Aufgaben</h2>
            <p>Entwicklung von Software...</p>
            <h2>Anforderungen</h2>
            <p>5 Jahre Erfahrung...</p>
            <h2>Wir bieten</h2>
            <p>Spannende Projekte...</p>
            <a href="#" class="apply-button">Jetzt bewerben</a>
        </div>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    analyzer = PageAnalyzer()
    
    # Test 1: Extract contacts
    print("\n1. Contact Extraction Test")
    print("-" * 80)
    contacts = analyzer.extract_contacts(soup)
    for i, contact in enumerate(contacts, 1):
        print(f"\n{i}. {contact.name}")
        if contact.title:
            print(f"   Title: {contact.title}")
        if contact.email:
            print(f"   Email: {contact.email}")
        if contact.phone:
            print(f"   Phone: {contact.phone}")
        print(f"   Confidence: {contact.confidence:.2f}")
    
    # Test 2: Extract addresses
    print("\n\n2. Address Extraction Test")
    print("-" * 80)
    addresses = analyzer.extract_addresses(soup, location_hint="Berlin")
    for i, addr in enumerate(addresses, 1):
        print(f"\n{i}. {addr.full_address or '(incomplete)'}")
        print(f"   Street: {addr.street or 'N/A'}")
        print(f"   Postal Code: {addr.postal_code or 'N/A'}")
        print(f"   City: {addr.city or 'N/A'}")
        print(f"   Confidence: {addr.confidence:.2f}")
    
    # Test 3: Job posting detection
    print("\n\n3. Job Posting Detection Test")
    print("-" * 80)
    is_job = analyzer.is_job_posting_page(soup)
    print(f"Is job posting: {is_job}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
