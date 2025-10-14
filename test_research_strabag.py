"""Test the research functionality to find STRABAG address"""
import sys
sys.path.insert(0, 'src')

from utils.web_search import WebSearcher
from utils.page_analyzer import PageAnalyzer
import json

# Load the scraped job data
with open('data/scraped_job_20251014_112725.json', encoding='utf-8') as f:
    job_data = json.load(f)

company_name = job_data['company_name']
location = job_data['location']
website = job_data.get('website_link')

print("="*80)
print("TESTING RESEARCH FUNCTIONALITY - FINDING COMPANY ADDRESS")
print("="*80)
print(f"Company: {company_name}")
print(f"Location: {location}")
print(f"Website: {website}")
print()

# Step 1: Search for company pages
print("="*80)
print("STEP 1: Searching for company career/contact pages")
print("="*80)
searcher = WebSearcher()
search_results = searcher.find_company_pages(
    company_name, 
    keywords=['karriere', 'jobs', 'kontakt', 'impressum']
)

print(f"\nFound {len(search_results)} relevant pages:")
for i, result in enumerate(search_results[:5], 1):
    print(f"\n{i}. {result.title}")
    print(f"   URL: {result.url}")
    print(f"   Relevance: {result.relevance_score:.2f}")
    print(f"   Snippet: {result.snippet[:150]}...")

# Step 2: Analyze pages for address
print("\n" + "="*80)
print("STEP 2: Analyzing pages for company address")
print("="*80)

analyzer = PageAnalyzer()
found_addresses = []

# Try the website first if available
if website:
    print(f"\nAnalyzing company website: {website}")
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(website, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'lxml')
        addresses = analyzer.extract_addresses(soup, location_hint=location)
        if addresses:
            print(f"  ✓ Found {len(addresses)} addresses on website")
            for addr in addresses[:3]:
                print(f"    - {addr.street}, {addr.postal_code} {addr.city} (confidence: {addr.confidence:.2f})")
                found_addresses.append(addr)
        else:
            print(f"  No addresses found on website")
    except Exception as e:
        print(f"  Error fetching website: {e}")

# Try search results (if any were found despite rate limit)
for result in search_results[:3]:
    print(f"\nAnalyzing: {result.url}")
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(result.url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'lxml')
        addresses = analyzer.extract_addresses(soup, location_hint=location)
        if addresses:
            print(f"  ✓ Found {len(addresses)} addresses")
            for addr in addresses[:2]:
                print(f"    - {addr.street}, {addr.postal_code} {addr.city} (confidence: {addr.confidence:.2f})")
                found_addresses.append(addr)
        else:
            print("  No addresses found")
    except Exception as e:
        print(f"  Error analyzing page: {e}")

# Step 3: Show best address
print("\n" + "="*80)
print("STEP 3: Best address found")
print("="*80)

if found_addresses:
    # Sort by confidence
    found_addresses.sort(key=lambda x: x.confidence, reverse=True)
    best = found_addresses[0]
    
    print(f"\nBest Match:")
    print(f"  Street: {best.street}")
    print(f"  Postal Code: {best.postal_code}")
    print(f"  City: {best.city}")
    print(f"  Country: {best.country}")
    print(f"  Confidence: {best.confidence:.2f}")
    
    print(f"\nFormatted:")
    print(f"  Line 1: {best.street}")
    print(f"  Line 2: {best.postal_code} {best.city}")
else:
    print("\n❌ No addresses found via research")

print("\n" + "="*80)
print("COMPARISON WITH SCRAPER")
print("="*80)
print(f"Scraper extracted:")
print(f"  Line 1: {job_data['company_address_line1']}")
print(f"  Line 2: {job_data['company_address_line2']}")
print(f"  Full: {job_data['company_address']}")
