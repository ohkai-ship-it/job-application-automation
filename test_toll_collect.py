"""Test scraper with Toll Collect job posting"""
import sys
sys.path.insert(0, 'src')

from scraper import scrape_stepstone_job
import json

url = 'https://www.stepstone.de/stellenangebote--Business-Engineer-Digitalisierung-d-m-w-Digitalisieren-Sie-Geschaeftsmodelle-mit-Strategie-Technologie-und-Innovation-Berlin-Toll-Collect-GmbH--13098287-inline.html?rltr=2_2_16_ma_rj_0_0_0_0_0'

print("="*80)
print("SCRAPING TOLL COLLECT JOB POSTING")
print("="*80)
print()

job_data = scrape_stepstone_job(url)

print("="*80)
print("COMPANY & ADDRESS INFO")
print("="*80)
print(f"Company: {job_data['company_name']}")
print(f"Location: {job_data['location']}")
print(f"Address Line 1: {job_data['company_address_line1']}")
print(f"Address Line 2: {job_data['company_address_line2']}")
print(f"Full Address: {job_data['company_address']}")
print()

print("="*80)
print("JOB DESCRIPTION - ADDRESS SECTIONS")
print("="*80)
lines = job_data['job_description'].split('\n')

for i, line in enumerate(lines):
    if 'Toll Collect' in line and i < len(lines)-5:
        print(f"\nLine {i}: {line}")
        for j in range(1, 6):
            if i+j < len(lines):
                print(f"  +{j}: {lines[i+j]}")

# Save for inspection
output_file = 'data/test_toll_collect.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(job_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"Full data saved to: {output_file}")
print("="*80)
