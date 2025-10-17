"""
Quick test script to process a job posting with placeholder mode
"""
import os
import sys

# Enable placeholder mode
os.environ['USE_PLACEHOLDER_COVER_LETTER'] = 'true'

sys.path.insert(0, 'src')
from main import process_job_posting

print("=" * 80)
print("TESTING JOB POSTING WITH PLACEHOLDER MODE")
print("=" * 80)
print()

url = "https://www.stepstone.de/stellenangebote--Manager-Strategy-Operations-Manager-Executive-Office-Berlin-Frankfurt-am-Main-Infopro-Digital--13103050-inline.html?rltr=ma_rj_0_0_0_0_0"

print(f"URL: {url}")
print(f"Placeholder Mode: {os.getenv('USE_PLACEHOLDER_COVER_LETTER')}")
print()

try:
    result = process_job_posting(url, generate_cover_letter=True, generate_pdf=True)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Company: {result['job_data'].get('company_name')}")
    print(f"Position: {result['job_data'].get('job_title')}")
    print(f"Location: {result['job_data'].get('location')}")
    print(f"Trello Card: {result.get('trello_card', {}).get('shortUrl', 'N/A')}")
    print(f"\nGenerated Files:")
    print(f"  Data File: {result.get('data_file', 'N/A')}")
    print(f"  Cover Letter TXT: {result.get('cover_letter_text_file', 'N/A')}")
    print(f"  Cover Letter DOCX: {result.get('cover_letter_docx_file', 'N/A')}")
    print(f"  Cover Letter PDF: {result.get('cover_letter_pdf_file', 'N/A')}")
    print("=" * 80)
    
    if result['status'] == 'success':
        print("\n✅ SUCCESS! All steps completed successfully.")
        
        # Read and display the cover letter preview
        txt_file = result.get('cover_letter_text_file')
        if txt_file and os.path.exists(txt_file):
            print("\n" + "=" * 80)
            print("COVER LETTER PREVIEW (First 300 chars)")
            print("=" * 80)
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:300] + "...")
                print(f"\nTotal words: {len(content.split())}")
            print("=" * 80)
    else:
        print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
