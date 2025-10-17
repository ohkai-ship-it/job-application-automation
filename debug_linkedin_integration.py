"""
LinkedIn Integration Debug Script

Use this after VS Code restart to systematically test the LinkedIn integration
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.linkedin_scraper import scrape_linkedin_job
from src.main import detect_job_source
import json

def test_url_detection():
    """Test URL detection"""
    print("\n" + "="*80)
    print("TEST 1: URL Detection")
    print("="*80)
    
    test_urls = [
        ("https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4294449394", "linkedin"),
        ("https://www.stepstone.de/stelle/...", "stepstone"),
    ]
    
    for url, expected in test_urls:
        result = detect_job_source(url)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: {url}")
        print(f"       Expected: {expected}, Got: {result}")

def test_scraper(url):
    """Test LinkedIn scraper"""
    print("\n" + "="*80)
    print(f"TEST 2: LinkedIn Scraper - {url[:60]}...")
    print("="*80)
    
    try:
        job_data = scrape_linkedin_job(url)
        
        if job_data:
            print("\n✓ Scraper returned data")
            print("\nExtracted Fields:")
            for key, value in job_data.items():
                if isinstance(value, str) and len(value) > 80:
                    print(f"  {key}: {value[:80]}... ({len(value)} chars)")
                else:
                    print(f"  {key}: {value}")
            return job_data
        else:
            print("\n✗ Scraper returned None")
            return None
    except Exception as e:
        print(f"\n✗ Scraper raised exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_config_values():
    """Test Trello config values"""
    print("\n" + "="*80)
    print("TEST 3: Trello Configuration")
    print("="*80)
    
    try:
        from src.utils.env import load_env, get_str
        load_env()
        
        config_keys = [
            'TRELLO_FIELD_QUELLE',
            'TRELLO_FIELD_QUELLE_STEPSTONE',
            'TRELLO_FIELD_QUELLE_LINKEDIN',
            'TRELLO_FIELD_AUSSCHREIBUNGSDATUM',
        ]
        
        print("\nConfiguration Values:")
        for key in config_keys:
            value = get_str(key, default='NOT SET')
            if value == 'NOT SET':
                print(f"  ✗ {key}: NOT SET")
            else:
                print(f"  ✓ {key}: {value[:50]}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False

def test_trello_connection():
    """Test Trello connection"""
    print("\n" + "="*80)
    print("TEST 4: Trello Connection")
    print("="*80)
    
    try:
        from src.trello_connect import TrelloConnect
        
        trello = TrelloConnect()
        
        print("\n✓ TrelloConnect initialized")
        print(f"  Board ID: {trello.board_id[:20]}...")
        print(f"  Quelle Field ID: {trello.field_source_list[:20] if trello.field_source_list else 'NOT SET'}...")
        print(f"  LinkedIn Option ID: {trello.field_source_linkedin_option[:20] if trello.field_source_linkedin_option else 'NOT SET'}...")
        
        return trello
    except Exception as e:
        print(f"✗ Error initializing Trello: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("LinkedIn Integration Debug Suite")
    print("="*80)
    
    # Test 1: URL Detection
    test_url_detection()
    
    # Test 3: Config
    test_config_values()
    
    # Test 4: Trello Connection
    trello = test_trello_connection()
    
    # Test 2: Scraper (with new URL)
    test_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4294449394"
    print("\n" + "="*80)
    print("Ready to test LinkedIn scraper with:")
    print(f"  {test_url}")
    print("\nNote: This may timeout if LinkedIn blocks the request")
    print("="*80 + "\n")
    
    input("Press Enter to test scraper (or Ctrl+C to skip)...")
    job_data = test_scraper(test_url)
    
    print("\n" + "="*80)
    print("Debug Suite Complete")
    print("="*80)
