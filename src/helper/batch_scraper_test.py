import sys
import os
sys.path.append(os.path.dirname(__file__))

from scraper import scrape_stepstone_job, save_to_json
import json
import time

def batch_test_scraper():
    """
    Test the scraper with multiple URLs to ensure robustness
    """
    
    test_urls = [
        {
            'name': 'LichtBlick - Technical Product Owner',
            'url': 'https://www.stepstone.de/stellenangebote--Technical-Product-Owner-gn-AI-Hamburg-LichtBlick-SE--13006068-inline.html?rltr=ma_jh_0_0_0_0_0'
        },
        {
            'name': 'Vaillant - Senior Product Owner',
            'url': 'https://www.stepstone.de/stellenangebote--Senior-Product-Owner-m-w-d-eCommerce-B2B-Webshop-Remscheid-Vaillant-GmbH--13040704-inline.html?rltr=ma_jh_0_0_0_0_0'
        },
        {
            'name': 'NETCONOMY - Senior Digital Strategy Consultant',
            'url': 'https://www.stepstone.de/stellenangebote--Senior-Digital-Strategy-Consultant-f-m-x-Berlin-Dortmund-NETCONOMY-GmbH--12822106-inline.html?rltr=ma_rj_0_0_0_0_0'
        },
        {
            'name': 'Toll Collect - Business Engineer',
            'url': 'https://www.stepstone.de/stellenangebote--Business-Engineer-Digitalisierung-d-m-w-Digitalisieren-Sie-Geschaeftsmodelle-mit-Strategie-Technologie-und-Innovation-Berlin-Toll-Collect-GmbH--13098287-inline.html?rltr=ma_rj_0_0_0_0_0'
        }
    ]
    
    results = []
    
    print("=" * 80)
    print("BATCH SCRAPER TEST")
    print("=" * 80)
    print(f"\nTesting {len(test_urls)} job postings...\n")
    
    for i, test in enumerate(test_urls, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}/{len(test_urls)}: {test['name']}")
        print("=" * 80)
        print(f"URL: {test['url']}\n")
        
        try:
            # Scrape the job
            job_data = scrape_stepstone_job(test['url'])
            
            if job_data:
                results.append({
                    'test_name': test['name'],
                    'status': 'SUCCESS',
                    'data': job_data
                })
                
                # Quick summary
                print("\n--- Quick Summary ---")
                print(f"Company: {job_data.get('company_name', 'N/A')}")
                print(f"Title: {job_data.get('job_title', 'N/A')[:80]}...")
                print(f"Location: {job_data.get('location', 'N/A')}")
                print(f"Date: {job_data.get('publication_date', 'N/A')}")
                print(f"Description length: {len(job_data.get('job_description', '')) if job_data.get('job_description') else 0} chars")
                print(f"Contact: {job_data.get('contact_person', {}).get('name', 'N/A')}")
                
                # Save individual result
                filename = f"data/job_{i}_{test['name'].replace(' ', '_').replace('-', '_')}.json"
                save_to_json(job_data, filename)
                
            else:
                results.append({
                    'test_name': test['name'],
                    'status': 'FAILED',
                    'error': 'Scraper returned None'
                })
                print("\n✗ FAILED: Scraper returned None")
                
        except Exception as e:
            results.append({
                'test_name': test['name'],
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n✗ ERROR: {e}")
        
        # Be polite - wait between requests
        if i < len(test_urls):
            print("\nWaiting 3 seconds before next request...")
            time.sleep(3)
    
    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] in ['FAILED', 'ERROR'])
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Success Rate: {(success_count/len(results)*100):.1f}%\n")
    
    # Detailed results
    print("--- Detailed Results ---\n")
    for i, result in enumerate(results, 1):
        status_icon = "✓" if result['status'] == 'SUCCESS' else "✗"
        print(f"{i}. {status_icon} {result['test_name']}: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            data = result['data']
            # Check data completeness
            fields = {
                'Company Name': data.get('company_name'),
                'Job Title': data.get('job_title'),
                'Location': data.get('location'),
                'Publication Date': data.get('publication_date'),
                'Job Description': data.get('job_description'),
                'Company Address': data.get('company_address')
            }
            
            missing = [k for k, v in fields.items() if not v]
            if missing:
                print(f"   Missing fields: {', '.join(missing)}")
            else:
                print(f"   ✓ All core fields extracted!")
        
        elif result['status'] in ['FAILED', 'ERROR']:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Save summary
    summary_file = 'data/batch_test_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(results),
            'successful': success_count,
            'failed': failed_count,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Summary saved to {summary_file}")
    
    return results


if __name__ == "__main__":
    batch_test_scraper()