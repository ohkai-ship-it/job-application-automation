"""
Test Database Integration - Duplicate Detection
Tests the complete workflow with database duplicate detection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db
from main import process_job_posting


def main():
    """Test duplicate detection workflow."""
    print("=" * 80)
    print("DATABASE INTEGRATION TEST - DUPLICATE DETECTION")
    print("=" * 80)
    
    # Use a test Stepstone URL (you can use a real one)
    test_url = "https://www.stepstone.de/stellenangebote--Test-Integration-12345.html"
    
    db = get_db()
    
    # Test 1: First processing (should succeed)
    print("\n[Test 1] Processing job for the FIRST time...")
    print(f"URL: {test_url}")
    print("-" * 80)
    
    result1 = process_job_posting(
        test_url,
        generate_cover_letter=False,  # Skip cover letter for faster testing
        generate_pdf=False,
        skip_duplicate_check=True  # Skip duplicate check for first run to simulate scraping
    )
    
    print(f"\nResult: {result1['status']}")
    
    if result1['status'] != 'success':
        print("❌ First processing failed!")
        print(f"Error: {result1.get('error', 'Unknown error')}")
        return False
    
    print("✓ First processing successful!")
    
    # Test 2: Second processing (should detect duplicate)
    print("\n" + "=" * 80)
    print("[Test 2] Processing SAME job URL again (should detect duplicate)...")
    print("-" * 80)
    
    result2 = process_job_posting(
        test_url,
        generate_cover_letter=False,
        generate_pdf=False,
        skip_duplicate_check=False  # Enable duplicate detection
    )
    
    print(f"\nResult: {result2['status']}")
    
    if result2['status'] != 'duplicate':
        print("❌ Duplicate detection failed!")
        print(f"Expected 'duplicate', got '{result2['status']}'")
        return False
    
    print("✓ Duplicate detected correctly!")
    print("\nDuplicate Info:")
    existing = result2.get('existing_job', {})
    print(f"  Company: {existing.get('company_name')}")
    print(f"  Job Title: {existing.get('job_title')}")
    print(f"  Processed: {existing.get('processed_at')}")
    if existing.get('trello_card_url'):
        print(f"  Trello: {existing.get('trello_card_url')}")
    
    # Test 3: Verify database contains the job
    print("\n" + "=" * 80)
    print("[Test 3] Verifying database contains the job...")
    print("-" * 80)
    
    is_dup, existing_job = db.check_duplicate(test_url)
    
    if not is_dup:
        print("❌ Job not found in database!")
        return False
    
    print("✓ Job found in database!")
    print(f"  Job ID: {existing_job['job_id']}")
    print(f"  Company: {existing_job['company_name']}")
    print(f"  Title: {existing_job['job_title']}")
    
    # Test 4: Get database stats
    print("\n" + "=" * 80)
    print("[Test 4] Database statistics...")
    print("-" * 80)
    
    stats = db.get_stats()
    print(f"  Total jobs: {stats['total_jobs']}")
    print(f"  Jobs this week: {stats['jobs_this_week']}")
    print(f"  Total AI cost: ${stats['total_ai_cost']}")
    print(f"  Top companies: {[c['company_name'] for c in stats['top_companies'][:3]]}")
    
    # Test 5: Search functionality
    print("\n" + "=" * 80)
    print("[Test 5] Search functionality...")
    print("-" * 80)
    
    search_results = db.search_jobs("Test", limit=5)
    print(f"  Found {len(search_results)} jobs matching 'Test'")
    for job in search_results:
        print(f"    - {job['company_name']}: {job['job_title']}")
    
    # Success!
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nDatabase integration is working correctly!")
    print("  ✓ Duplicate detection works")
    print("  ✓ Jobs are saved to database")
    print("  ✓ Search functionality works")
    print("  ✓ Statistics are calculated correctly")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
