"""
Test Flask App End-to-End
Simulates submitting a job URL and checking status
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def test_flask_workflow():
    print("="*80)
    print("FLASK APP END-TO-END TEST")
    print("="*80)
    
    # Test job URL
    test_url = "https://www.stepstone.de/stellenangebote--Bereichsleiter-Produktmanagement-m-w-d-Stuttgart-Dr-Maier-Partner-Executive-Search-GmbH--13132777-inline.html?rltr=ma_rj_0_0_0_0_0"
    
    print(f"\n1. Submitting job URL to Flask app...")
    print(f"   URL: {test_url[:80]}...")
    
    # Submit job
    response = requests.post(f"{BASE_URL}/process", json={"url": test_url})
    
    if response.status_code != 200:
        print(f"❌ Failed to submit: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    job_id = result.get('job_id')
    
    if not job_id:
        print(f"❌ No job_id returned")
        return False
    
    print(f"✅ Job submitted: {job_id}")
    
    # Poll for status
    print(f"\n2. Polling for completion...")
    
    max_attempts = 30  # 30 seconds max
    for attempt in range(max_attempts):
        time.sleep(1)
        
        status_response = requests.get(f"{BASE_URL}/status/{job_id}")
        
        if status_response.status_code != 200:
            print(f"❌ Status check failed: {status_response.status_code}")
            return False
        
        status_data = status_response.json()
        current_status = status_data.get('status')
        message = status_data.get('message', '')
        progress = status_data.get('progress', 0)
        
        print(f"   [{attempt+1:2d}s] Status: {current_status:12s} | Progress: {progress:3d}% | {message}")
        
        if current_status == 'complete':
            print(f"\n✅ Processing complete!")
            
            # Show results
            result_data = status_data.get('result', {})
            print(f"\n3. Results:")
            print(f"   Company: {result_data.get('company')}")
            print(f"   Title: {result_data.get('title')}")
            print(f"   Location: {result_data.get('location')}")
            print(f"   Trello: {result_data.get('trello_card')}")
            
            files = result_data.get('files', {})
            docx_file = files.get('docx')
            
            if docx_file:
                print(f"\n✅ DOCX file: {docx_file}")
                
                # Check if file actually exists
                import os
                if os.path.exists(docx_file):
                    size = os.path.getsize(docx_file)
                    print(f"   File size: {size:,} bytes")
                    print(f"\n🎉 SUCCESS! Cover letter generated and saved.")
                    return True
                else:
                    print(f"   ⚠️  File not found on disk!")
                    return False
            else:
                print(f"\n❌ No DOCX file in result")
                return False
        
        elif current_status == 'error':
            print(f"\n❌ Processing failed: {message}")
            return False
    
    print(f"\n❌ Timeout waiting for completion")
    return False

if __name__ == "__main__":
    print("\nMake sure Flask app is running:")
    print("  python src/app.py")
    print("\nThen run this test in another terminal.\n")
    
    input("Press Enter when Flask is ready...")
    
    try:
        # Test connection
        response = requests.get(BASE_URL)
        print(f"✅ Flask app is running\n")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Flask app at {BASE_URL}")
        print(f"   Make sure it's running: python src/app.py")
        exit(1)
    
    success = test_flask_workflow()
    
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED - Flask app working correctly!")
    else:
        print("❌ TEST FAILED - Check logs above")
    print("="*80)
