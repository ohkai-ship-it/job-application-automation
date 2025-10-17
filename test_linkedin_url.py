"""
Test LinkedIn scraper with specific URL
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.linkedin_scraper import scrape_linkedin_job

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4294449394"

print(f"Scraping: {url}")
print("=" * 80)

job_data = scrape_linkedin_job(url)

if job_data:
    print("\nEXTRACTED DATA:")
    print("=" * 80)
    for key, value in job_data.items():
        if isinstance(value, str) and len(value) > 150:
            print(f"\n{key.upper()}:")
            print(f"  {value[:150]}...")
            print(f"  [Total length: {len(value)} chars]")
        else:
            print(f"{key.upper()}: {value}")
else:
    print("Failed to scrape job data")
