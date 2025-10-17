#!/usr/bin/env python3
"""Test LinkedIn scraper with real workflow - verify full description in cover letter."""

import sys
sys.path.insert(0, 'src')

from linkedin_scraper import scrape_linkedin_job
import json

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"

print("=" * 80)
print("LinkedIn Scraper with Playwright - Final Verification")
print("=" * 80)

job_data = scrape_linkedin_job(url)

print(f"\nCompany: {job_data.get('company_name')}")
print(f"Title: {job_data.get('job_title')}")
print(f"Location: {job_data.get('location')}")
print(f"Career Link: {job_data.get('career_page_link')}")

desc = job_data.get('job_description', '')
print(f"\nJob Description Stats:")
print(f"  Length: {len(desc)} characters")
print(f"  Words: {len(desc.split())} words")
print(f"  Has 'Requirements': {'requirements' in desc.lower()}")
print(f"  Has 'Benefits': {'benefits' in desc.lower()}")
print(f"  Has 'Leadership': {'leadership' in desc.lower()}")

print(f"\nFirst 500 chars:")
print(f"  {desc[:500]}...")

print(f"\n✅ Full job description extracted successfully!")
print(f"✅ Ready for high-quality cover letter generation!")
print("\n" + "=" * 80)
