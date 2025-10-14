"""Test full workflow with Toll Collect job posting"""
import os
os.environ['USE_PLACEHOLDER_COVER_LETTER'] = 'true'

import sys
sys.path.insert(0, 'src')

from main import process_job_posting

url = 'https://www.stepstone.de/stellenangebote--Business-Engineer-Digitalisierung-d-m-w-Digitalisieren-Sie-Geschaeftsmodelle-mit-Strategie-Technologie-und-Innovation-Berlin-Toll-Collect-GmbH--13098287-inline.html?rltr=2_2_16_ma_rj_0_0_0_0_0'

print("="*80)
print("TESTING TOLL COLLECT JOB POSTING WITH PLACEHOLDER MODE")
print("="*80)
print(f"\nURL: {url}")
print(f"Placeholder Mode: {os.getenv('USE_PLACEHOLDER_COVER_LETTER')}")
print()

result = process_job_posting(url)

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"Status: {result['status']}")
print(f"Company: {result['company_name']}")
print(f"Position: {result['job_title']}")
print(f"Location: {result['location']}")

if result['status'] == 'success':
    print(f"\nGenerated Files:")
    print(f"  Data File: {result['data_file']}")
    print(f"  Cover Letter TXT: {result['cover_letter_txt']}")
    print(f"  Cover Letter DOCX: {result['cover_letter_docx']}")
    print(f"  Cover Letter PDF: {result['cover_letter_pdf']}")
    print("="*80)
    print()
    print("✅ SUCCESS! All steps completed successfully.")
else:
    print(f"\n❌ Error: {result.get('error', 'Unknown error')}")

print()
