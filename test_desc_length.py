#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from linkedin_scraper import scrape_linkedin_job

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"
data = scrape_linkedin_job(url)

desc_len = len(data.get("job_description", "")) if data else 0
print(f"Description length: {desc_len} chars")
if desc_len > 100:
    print(f"Preview: {data.get('job_description', '')[:200]}...")
