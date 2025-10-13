"""
Test script to verify custom field population on a real Stepstone job.
"""
import sys
sys.path.insert(0, 'src')

from scraper import scrape_stepstone_job
from trello_connect import TrelloConnect

# Test with a real Stepstone URL
test_url = "https://www.stepstone.de/stellenangebote--AI-Product-Owner-Operations-and-Supply-Chain-f-m-d-Hilden-QIAGEN-GmbH--12300854-inline.html"

print("="*70)
print("Testing Custom Field Population")
print("="*70)

# Step 1: Scrape the job
print("\n1. Scraping job posting...")
job_data = scrape_stepstone_job(test_url)

if not job_data:
    print("✗ Failed to scrape job")
    sys.exit(1)

print(f"✓ Scraped: {job_data.get('company_name')} - {job_data.get('job_title')}")
print(f"  Publication Date: {job_data.get('publication_date', 'N/A')}")

# Step 2: Create Trello card
print("\n2. Creating Trello card with custom fields...")
tc = TrelloConnect()
result = tc.create_card_from_job_data(job_data)

if result:
    if result.get('already_exists'):
        print(f"✓ Card already exists: {result.get('id')}")
    else:
        print(f"✓ Card created: {result.get('shortUrl')}")
        print(f"\n3. Verifying custom fields...")
        print(f"   Run: python inspect_card.py")
        print(f"   to verify the custom fields were set correctly")
else:
    print("✗ Failed to create card")

print("\n" + "="*70)
