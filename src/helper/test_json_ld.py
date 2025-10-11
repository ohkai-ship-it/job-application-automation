import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

def scrape_stepstone_job(url):
    """
    Scrapes a Stepstone job posting and extracts key information.
    
    Args:
        url (str): The URL of the Stepstone job posting
        
    Returns:
        dict: Dictionary containing extracted job information
    """
    
    # Initialize result dictionary
    job_data = {
        'company_name': None,
        'company_address': None,
        'job_title': None,
        'location': None,
        'work_mode': None,  # office/hybrid/remote
        'website_link': None,
        'career_page_link': None,
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
    
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Fetch the page
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        print("✓ Page fetched successfully!")
        print("\n--- Extracting Data ---")
        
        # STRATEGY 1: Extract from JSON-LD (most reliable!)
        json_ld_data = None
        json_ld_script = soup.find('script', type='application/ld+json')
        if json_ld_script and json_ld_script.string:
            try:
                json_ld_data = json.loads(json_ld_script.string)
                print("✓ Found JSON-LD structured data!")
                print(f"  JSON-LD Type: {json_ld_data.get('@type', 'unknown')}")
            except Exception as e:
                print(f"✗ Failed to parse JSON-LD: {e}")
        else:
            print("✗ No JSON-LD found in page")
        
        # STRATEGY 2: Use data-at attributes (Stepstone specific)
        
        # 1. Job Title
        if json_ld_data and 'title' in json_ld_data:
            job_data['job_title'] = json_ld_data['title']
        else:
            title_tag = soup.find(attrs={'data-at': 'header-job-title'})
            if title_tag:
                job_data['job_title'] = title_tag.get_text(strip=True)
        
        if job_data['job_title']:
            print(f"✓ Job Title: {job_data['job_title']}")
        
        # 2. Company Name
        if json_ld_data and 'hiringOrganization' in json_ld_data:
            job_data['company_name'] = json_ld_data['hiringOrganization'].get('name')
        else:
            company_tag = soup.find(attrs={'data-at': 'metadata-company-name'})
            if company_tag:
                job_data['company_name'] = company_tag.get_text(strip=True)
        
        if job_data['company_name']:
            print(f"✓ Company: {job_data['company_name']}")
        
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
            print(f"✓ Location: {job_data['location']}")
        
        # 4. Work Mode (office/hybrid/remote)
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
            print(f"✓ Work Mode: {job_data['work_mode']}")
        
        # 5. Publication Date
        if json_ld_data and 'datePosted' in json_ld_data:
            job_data['publication_date'] = json_ld_data['datePosted']
            print(f"✓ Publication Date: {job_data['publication_date']}")
        else:
            date_tag = soup.find(attrs={'data-at': 'metadata-online-date'})
            if date_tag:
                job_data['publication_date'] = date_tag.get_text(strip=True)
                print(f"✓ Publication Date: {job_data['publication_date']}")
        
        # 6. Job Description
        if json_ld_data and 'description' in json_ld_data:
            # JSON-LD description is usually HTML, clean it up
            desc_html = json_ld_data['description']
            desc_soup = BeautifulSoup(desc_html, 'lxml')
            job_data['job_description'] = desc_soup.get_text(separator='\n', strip=True)
            desc_preview = job_data['job_description'][:200] + "..."
            print(f"✓ Job Description: {desc_preview}")
        
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
                    print(f"✓ Company Address: {job_data['company_address']}")
        
        # 8. Website Link
        if json_ld_data and 'hiringOrganization' in json_ld_data:
            org = json_ld_data['hiringOrganization']
            if 'url' in org:
                job_data['website_link'] = org['url']
                print(f"✓ Website Link: {job_data['website_link']}")
        
        # 9. Career Page Link (look for it in the page)
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            
            if 'karriere' in link_text or 'career' in link_text:
                # Make absolute URL if relative
                if href.startswith('/'):
                    job_data['career_page_link'] = 'https://www.stepstone.de' + href
                else:
                    job_data['career_page_link'] = href
                print(f"✓ Career Page: {job_data['career_page_link']}")
                break
        
        # 10. Contact Information
        # Look for email in the job description or page
        page_text = soup.get_text()
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
        # Filter out common generic emails
        emails = [e for e in emails if not any(x in e.lower() for x in ['beispiel', 'example', 'noreply', 'privacy'])]
        if emails:
            job_data['contact_person']['email'] = emails[0]
            print(f"✓ Contact Email: {job_data['contact_person']['email']}")
        
        # Look for phone numbers
        phones = re.findall(r'\+?\d{2,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}', page_text)
        # Filter out dates and years
        phones = [p for p in phones if len(p.replace(' ', '').replace('-', '')) > 8]
        if phones:
            job_data['contact_person']['phone'] = phones[0].strip()
            print(f"✓ Contact Phone: {job_data['contact_person']['phone']}")
        
        # Look for contact name
        contact_keywords = ['ansprechpartner', 'kontakt', 'recruiter', 'ihre ansprechperson']
        for keyword in contact_keywords:
            contact_section = soup.find(string=re.compile(keyword, re.I))
            if contact_section:
                parent = contact_section.find_parent()
                if parent:
                    # Look for name patterns in next siblings or children
                    text = parent.get_text()
                    # Simple name pattern: Two capitalized words
                    name_match = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)\b', text)
                    if name_match:
                        job_data['contact_person']['name'] = name_match.group(1)
                        print(f"✓ Contact Name: {job_data['contact_person']['name']}")
                        break
        
        print("\n✓ Scraping completed successfully!")
        return job_data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching page: {e}")
        return None
    except Exception as e:
        print(f"✗ Error parsing page: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_to_json(data, filename='job_data.json'):
    """Save scraped data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Data saved to {filename}")


# Test function
if __name__ == "__main__":
    # Test URL
    test_url = "https://www.stepstone.de/stellenangebote--Business-Engineer-Digitalisierung-d-m-w-Digitalisieren-Sie-Geschaeftsmodelle-mit-Strategie-Technologie-und-Innovation-Berlin-Toll-Collect-GmbH--13098287-inline.html"
    
    print("=== Stepstone Job Scraper (Improved) ===\n")
    
    result = scrape_stepstone_job(test_url)
    
    if result:
        print("\n=== Final Extracted Data ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Save to file
        save_to_json(result, 'data/job_data.json')
    else:
        print("\n✗ Scraping failed!")