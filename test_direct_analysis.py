"""Direct analysis of STRABAG career/contact pages"""
import sys
sys.path.insert(0, 'src')

from utils.page_analyzer import PageAnalyzer
import requests
from bs4 import BeautifulSoup
import json

# Load job data
with open('data/scraped_job_20251014_112725.json', encoding='utf-8') as f:
    job_data = json.load(f)

print("="*80)
print("DIRECT PAGE ANALYSIS - STRABAG")
print("="*80)

analyzer = PageAnalyzer()

# URLs to try
urls_to_try = [
    ('Career Page', job_data.get('career_page_link')),
    ('Main Website', job_data.get('website_link')),
    ('Impressum', 'https://www.strabag.de/impressum.html'),
    ('Kontakt', 'https://www.strabag.de/kontakt.html'),
]

all_addresses = []

for name, url in urls_to_try:
    if not url:
        continue
        
    print(f"\n{'='*80}")
    print(f"Analyzing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            continue
            
        soup = BeautifulSoup(response.content, 'lxml')
        addresses = analyzer.extract_addresses(soup, location_hint='Stuttgart')
        
        if addresses:
            print(f"  ✓ Found {len(addresses)} addresses:")
            for addr in addresses:
                print(f"\n    Address:")
                print(f"      Street: {addr.street}")
                print(f"      Postal: {addr.postal_code}")
                print(f"      City: {addr.city}")
                print(f"      Country: {addr.country}")
                print(f"      Confidence: {addr.confidence:.2f}")
                all_addresses.append((name, url, addr))
        else:
            print(f"  No addresses found")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Summary
print("\n" + "="*80)
print("SUMMARY - ALL FOUND ADDRESSES")
print("="*80)

if all_addresses:
    # Sort by confidence
    all_addresses.sort(key=lambda x: x[2].confidence, reverse=True)
    
    for i, (source, url, addr) in enumerate(all_addresses, 1):
        print(f"\n{i}. From: {source}")
        print(f"   URL: {url}")
        print(f"   Address: {addr.street}, {addr.postal_code} {addr.city}")
        print(f"   Confidence: {addr.confidence:.2f}")
    
    print("\n" + "="*80)
    print("BEST MATCH")
    print("="*80)
    best_source, best_url, best_addr = all_addresses[0]
    print(f"Source: {best_source}")
    print(f"Address Line 1: {best_addr.street}")
    print(f"Address Line 2: {best_addr.postal_code} {best_addr.city}")
else:
    print("\n❌ No addresses found on any page")

print("\n" + "="*80)
print("COMPARISON WITH SCRAPER")
print("="*80)
print(f"Scraper extracted from job description:")
print(f"  Line 1: '{job_data['company_address_line1']}'")
print(f"  Line 2: '{job_data['company_address_line2']}'")
print(f"  Full: '{job_data['company_address']}'")
