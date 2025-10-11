"""
Main workflow for job application automation.
Scrapes Stepstone job postings, creates Trello cards, generates cover letters, and creates PDFs.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from scraper import scrape_stepstone_job, save_to_json
from trello_connect import TrelloConnect
from cover_letter import CoverLetterGenerator
from docx_generator import WordCoverLetterGenerator
from utils.env import load_env, get_str, validate_env
import json
from datetime import datetime

# Validate environment at startup
try:
    from utils.env import validate_all_env
    validate_all_env()
except ValueError as e:
    print("\n⚠️  Environment Validation Error:")
    print(str(e))
    sys.exit(1)
except Exception as e:
    print(f"\n⚠️  Unexpected error during environment validation: {e}")
    sys.exit(1)

# Get configured paths
DATA_DIR = Path(get_str('DATA_DIR', 'data'))
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))


def process_job_posting(url, generate_cover_letter=True, generate_pdf=True):
    """
    Complete workflow: Scrape job posting, create Trello card, generate cover letter and PDF
    
    Args:
        url (str): Stepstone job posting URL
        generate_cover_letter (bool): Whether to generate a cover letter
        generate_pdf (bool): Whether to convert to PDF
        
    Returns:
        dict: Result with status and data
    """
    
    print("=" * 80)
    print("JOB APPLICATION AUTOMATION")
    print("=" * 80)
    print(f"\nProcessing: {url}\n")
    
    # Step 1: Scrape the job posting
    print("STEP 1: Scraping job posting...")
    print("-" * 80)
    
    job_data = scrape_stepstone_job(url)
    
    if not job_data:
        print("\n✗ Failed to scrape job posting!")
        return {
            'status': 'failed',
            'step': 'scraping',
            'error': 'Scraper returned no data'
        }
    
    print(f"\n✓ Successfully scraped job data!")
    
    # Save scraped data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = DATA_DIR / f"scraped_job_{timestamp}.json"
    save_to_json(job_data, str(filename))
    
    # Step 2: Create Trello card
    print("\n" + "=" * 80)
    print("STEP 2: Creating Trello card...")
    print("-" * 80)
    
    trello = TrelloConnect()
    card = trello.create_card_from_job_data(job_data)
    
    if not card:
        print("\n✗ Failed to create Trello card!")
        return {
            'status': 'partial',
            'step': 'trello',
            'job_data': job_data,
            'error': 'Failed to create card'
        }
    
    # Step 3: Generate cover letter (optional)
    cover_letter_text = None
    cover_letter_file = None
    docx_file = None
    pdf_file = None
    
    if generate_cover_letter:
        print("\n" + "=" * 80)
        print("STEP 3: Generating cover letter...")
        print("-" * 80)
        
        try:
            # Generate AI text
            ai_generator = CoverLetterGenerator()
            cover_letter_text = ai_generator.generate_cover_letter(job_data)
            
            # Detect language
            language = ai_generator.detect_language(job_data.get('job_description', ''))
            
            # Display preview
            print("\n--- Cover Letter Preview ---")
            preview = cover_letter_text[:300] + "..." if len(cover_letter_text) > 300 else cover_letter_text
            print(preview)
            print("-" * 80)
            
            # Save text version
            cover_letter_file = ai_generator.save_cover_letter(cover_letter_text, job_data)
            
            # Step 4: Generate Word document
            print("\n" + "=" * 80)
            print("STEP 4: Creating Word document...")
            print("-" * 80)
            
            word_generator = WordCoverLetterGenerator()
            company = job_data.get('company_name', 'Company').replace(' ', '_')
            docx_filename = f"output/cover_letters/CoverLetter_{company}_{timestamp}.docx"
            
            docx_file = word_generator.generate_from_template(
                cover_letter_text,
                job_data,
                docx_filename,
                language=language
            )
            
            # Step 5: Convert to PDF (optional)
            if generate_pdf:
                print("\n" + "=" * 80)
                print("STEP 5: Converting to PDF...")
                print("-" * 80)
                
                pdf_filename = docx_filename.replace('.docx', '.pdf')
                pdf_file = word_generator.convert_to_pdf(docx_file, pdf_filename)
                
                if not pdf_file:
                    print("⚠ PDF conversion skipped - install with: pip install docx2pdf")
            
        except Exception as e:
            print(f"\n⚠ Warning: Cover letter generation failed: {e}")
            print("Continuing without cover letter...")
            import traceback
            traceback.print_exc()
    
    # Success!
    print("\n" + "=" * 80)
    print("✓ AUTOMATION COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"  Company: {job_data.get('company_name', 'N/A')}")
    print(f"  Position: {job_data.get('job_title', 'N/A')}")
    print(f"  Location: {job_data.get('location', 'N/A')}")
    print(f"  Trello Card: {card['shortUrl']}")
    print(f"  Data saved: {filename}")
    if cover_letter_file:
        print(f"  Cover Letter (TXT): {cover_letter_file}")
    if docx_file:
        print(f"  Cover Letter (DOCX): {docx_file}")
    if pdf_file:
        print(f"  Cover Letter (PDF): {pdf_file}")
    
    return {
        'status': 'success',
        'job_data': job_data,
        'trello_card': card,
        'data_file': filename,
        'cover_letter_text_file': cover_letter_file,
        'cover_letter_docx_file': docx_file,
        'cover_letter_pdf_file': pdf_file
    }


def batch_process_urls(urls):
    """
    Process multiple job posting URLs
    
    Args:
        urls (list): List of Stepstone URLs
        
    Returns:
        list: Results for each URL
    """
    
    results = []
    
    print("=" * 80)
    print(f"BATCH PROCESSING {len(urls)} JOB POSTINGS")
    print("=" * 80)
    
    for i, url in enumerate(urls, 1):
        print(f"\n\n{'='*80}")
        print(f"Processing {i}/{len(urls)}")
        print(f"{'='*80}\n")
        
        result = process_job_posting(url)
        results.append({
            'url': url,
            **result
        })
        
        # Wait between requests (be polite to Stepstone)
        if i < len(urls):
            import time
            print("\nWaiting 3 seconds before next job...")
            time.sleep(3)
    
    # Final summary
    print("\n\n" + "=" * 80)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\nResults: {successful}/{len(urls)} successful")
    
    for i, result in enumerate(results, 1):
        status_icon = "✓" if result['status'] == 'success' else "✗"
        company = result.get('job_data', {}).get('company_name', 'Unknown') if 'job_data' in result else 'Unknown'
        print(f"{i}. {status_icon} {company}")
        if result['status'] == 'success':
            print(f"   Card: {result['trello_card']['shortUrl']}")
    
    return results


def interactive_mode():
    """
    Interactive command-line interface
    """
    
    print("=" * 80)
    print("JOB APPLICATION AUTOMATION - Interactive Mode")
    print("=" * 80)
    
    while True:
        print("\nOptions:")
        print("  1. Process single job posting")
        print("  2. Process multiple job postings")
        print("  3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            url = input("\nEnter Stepstone job URL: ").strip()
            if url:
                process_job_posting(url)
            else:
                print("✗ No URL provided!")
        
        elif choice == '2':
            print("\nEnter Stepstone URLs (one per line, empty line to finish):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                batch_process_urls(urls)
            else:
                print("✗ No URLs provided!")
        
        elif choice == '3':
            print("\nGoodbye!")
            break
        
        else:
            print("✗ Invalid option!")


if __name__ == "__main__":
    # Check if URL provided as command line argument
    if len(sys.argv) > 1:
        # Command line mode
        urls = sys.argv[1:]
        
        if len(urls) == 1:
            process_job_posting(urls[0])
        else:
            batch_process_urls(urls)
    else:
        # Interactive mode
        interactive_mode()