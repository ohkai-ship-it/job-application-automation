#!/usr/bin/env python3
"""Quick test of the new LinkedIn URL."""

import sys
sys.path.insert(0, 'src')

from linkedin_scraper import scrape_linkedin_job
import json

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"

print(f"Testing URL: {url}\n")
print("=" * 80)

try:
    job_data = scrape_linkedin_job(url)
    print("\n✅ Scraper returned data:\n")
    print(json.dumps(job_data, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("\n📋 Data Summary:")
    print(f"  Company: {job_data.get('company_name', 'N/A')}")
    print(f"  Title: {job_data.get('job_title', 'N/A')}")
    print(f"  Location: {job_data.get('location', 'N/A')}")
    print(f"  Address: {job_data.get('company_address', 'N/A')}")
    print(f"  Career Link: {job_data.get('career_page_link', 'N/A')}")
    print(f"  Description length: {len(job_data.get('job_description', ''))} chars")
    print(f"\n  Description preview:\n  {job_data.get('job_description', 'N/A')[:200]}...")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
