"""Test new filename format"""
import os
os.environ['USE_PLACEHOLDER_COVER_LETTER'] = 'true'

import sys
sys.path.insert(0, 'src')

from main import process_job_posting

print("="*80)
print("TESTING NEW FILENAME FORMAT")
print("="*80)

# Test with an English job posting
url = 'https://www.stepstone.de/stellenangebote--Business-Engineer-Digitalisierung-d-m-w-Digitalisieren-Sie-Geschaeftsmodelle-mit-Strategie-Technologie-und-Innovation-Berlin-Toll-Collect-GmbH--13098287-inline.html'

print(f"\nProcessing: {url[:100]}...")
result = process_job_posting(url)

if result['status'] == 'success':
    print("\n✅ SUCCESS!")
    print(f"\nGenerated files:")
    print(f"  DOCX: {result.get('cover_letter_docx_file')}")
    print(f"  PDF:  {result.get('cover_letter_pdf_file')}")
    
    # Check if the new format is used
    docx_file = result.get('cover_letter_docx_file', '')
    if 'Cover letter - Dr. Kai Voges' in docx_file:
        print("\n✅ New filename format working correctly!")
    else:
        print(f"\n❌ Old filename format still in use: {docx_file}")
else:
    print(f"\n❌ Error: {result.get('error')}")
