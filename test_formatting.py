#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from linkedin_scraper import scrape_linkedin_job, format_linkedin_description

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"
data = scrape_linkedin_job(url)

desc = data.get("job_description", "")
print("=" * 80)
print("Formatted LinkedIn Job Description Preview")
print("=" * 80)
print(f"\nLength: {len(desc)} chars")
print(f"\nFormatted description (first 800 chars):\n")
print(desc[:800])
print("\n...")
print("\nNotice:")
print("- Line breaks between sections for readability")
print("- Emojis removed")
print("- Logical paragraph grouping")
print("=" * 80)
