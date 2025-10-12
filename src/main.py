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
from utils.logging import get_logger
from utils.error_reporting import report_error
import json
from datetime import datetime

# Validate environment at startup (allow skipping in tests)
skip_env = os.getenv('SKIP_ENV_VALIDATION', '0') == '1'
logger = get_logger(__name__)
if not skip_env:
    try:
        from utils.env import validate_all_env
        validate_all_env()
    except ValueError as e:
        logger.error("Environment Validation Error: %s", str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during environment validation: %s", e)
        sys.exit(1)

# Get configured paths
DATA_DIR = Path(get_str('DATA_DIR', 'data'))
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))


from typing import Any, Dict, List, Optional

def process_job_posting(
    url: str,
    generate_cover_letter: bool = True,
    generate_pdf: bool = True
) -> Dict[str, Any]:
    """
    Complete workflow: Scrape job posting, create Trello card, generate cover letter and PDF
    
    Args:
        url (str): Stepstone job posting URL
        generate_cover_letter (bool): Whether to generate a cover letter
        generate_pdf (bool): Whether to convert to PDF
        
    Returns:
        dict: Result with status and data
    """
    
    logger.info("%s", "=" * 80)
    logger.info("JOB APPLICATION AUTOMATION")
    logger.info("%s", "=" * 80)
    logger.info("Processing: %s", url)
    
    # Step 1: Scrape the job posting
    logger.info("STEP 1: Scraping job posting...")
    logger.info("%s", "-" * 80)
    
    job_data = scrape_stepstone_job(url)
    
    if not job_data:
        logger.error("Failed to scrape job posting!")
        # Record structured error for diagnostics
        report_error(
            "Scrape returned no data",
            context={"url": url},
            severity="error",
        )
        return {
            'status': 'failed',
            'step': 'scraping',
            'error': 'Scraper returned no data'
        }
    
    logger.info("Successfully scraped job data!")
    
    # Save scraped data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = DATA_DIR / f"scraped_job_{timestamp}.json"
    save_to_json(job_data, str(filename))
    
    # Step 2: Create Trello card
    logger.info("%s", "=" * 80)
    logger.info("STEP 2: Creating Trello card...")
    logger.info("%s", "-" * 80)
    
    trello = TrelloConnect()
    card = trello.create_card_from_job_data(job_data)
    
    if not card:
        logger.error("Failed to create Trello card!")
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
        logger.info("%s", "=" * 80)
        logger.info("STEP 3: Generating cover letter...")
        logger.info("%s", "-" * 80)
        
        try:
            # Generate AI text
            ai_generator = CoverLetterGenerator()
            cover_letter_text = ai_generator.generate_cover_letter(job_data)
            
            # Detect language
            language = ai_generator.detect_language(job_data.get('job_description', ''))
            
            # Display preview
            logger.info("--- Cover Letter Preview ---")
            preview = cover_letter_text[:300] + "..." if len(cover_letter_text) > 300 else cover_letter_text
            logger.info("%s", preview)
            logger.info("%s", "-" * 80)
            
            # Save text version
            cover_letter_file = ai_generator.save_cover_letter(cover_letter_text, job_data)
            
            # Step 4: Generate Word document
            logger.info("%s", "=" * 80)
            logger.info("STEP 4: Creating Word document...")
            logger.info("%s", "-" * 80)
            
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
                logger.info("%s", "=" * 80)
                logger.info("STEP 5: Converting to PDF...")
                logger.info("%s", "-" * 80)
                
                pdf_filename = docx_filename.replace('.docx', '.pdf')
                pdf_file = word_generator.convert_to_pdf(docx_file, pdf_filename)
                
                if not pdf_file:
                    logger.warning("PDF conversion skipped - install with: pip install docx2pdf")
            
        except Exception as e:
            logger.warning("Cover letter generation failed: %s", e)
            report_error(
                "Cover letter generation failed",
                exc=e,
                context={
                    "company": job_data.get('company_name'),
                    "title": job_data.get('job_title'),
                    "url": job_data.get('source_url'),
                },
                severity="error",
            )
            logger.info("Continuing without cover letter...")
            import traceback
            logger.debug("Traceback:")
            logger.debug("%s", traceback.format_exc())
    
    # Success!
    logger.info("%s", "=" * 80)
    logger.info("AUTOMATION COMPLETE!")
    logger.info("%s", "=" * 80)

    logger.info("Summary:")
    logger.info("  Company: %s", job_data.get('company_name', 'N/A'))
    logger.info("  Position: %s", job_data.get('job_title', 'N/A'))
    logger.info("  Location: %s", job_data.get('location', 'N/A'))
    logger.info("  Trello Card: %s", card['shortUrl'])
    logger.info("  Data saved: %s", filename)
    if cover_letter_file:
        logger.info("  Cover Letter (TXT): %s", cover_letter_file)
    if docx_file:
        logger.info("  Cover Letter (DOCX): %s", docx_file)
    if pdf_file:
        logger.info("  Cover Letter (PDF): %s", pdf_file)
    
    return {
        'status': 'success',
        'job_data': job_data,
        'trello_card': card,
        'data_file': filename,
        'cover_letter_text_file': cover_letter_file,
        'cover_letter_docx_file': docx_file,
        'cover_letter_pdf_file': pdf_file
    }


def batch_process_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Process multiple job posting URLs
    
    Args:
        urls (list): List of Stepstone URLs
        
    Returns:
        list: Results for each URL
    """
    
    results = []
    
    logger.info("%s", "=" * 80)
    logger.info("BATCH PROCESSING %s JOB POSTINGS", len(urls))
    logger.info("%s", "=" * 80)
    
    for i, url in enumerate(urls, 1):
        logger.info("%s", "=" * 80)
        logger.info("Processing %s/%s", i, len(urls))
        logger.info("%s", "=" * 80)
        
        result = process_job_posting(url)
        results.append({
            'url': url,
            **result
        })
        
        # Wait between requests (be polite to Stepstone)
        if i < len(urls):
            import time
            logger.info("Waiting 3 seconds before next job...")
            time.sleep(3)
    
    # Final summary
    logger.info("%s", "=" * 80)
    logger.info("BATCH PROCESSING COMPLETE")
    logger.info("%s", "=" * 80)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    logger.info("Results: %s/%s successful", successful, len(urls))
    
    for i, result in enumerate(results, 1):
        status_icon = "✓" if result['status'] == 'success' else "✗"
        company = result.get('job_data', {}).get('company_name', 'Unknown') if 'job_data' in result else 'Unknown'
        logger.info("%s. %s %s", i, status_icon, company)
        if result['status'] == 'success':
            logger.info("   Card: %s", result['trello_card']['shortUrl'])
    
    return results


def interactive_mode() -> None:
    """
    Interactive command-line interface
    """
    
    logger.info("%s", "=" * 80)
    logger.info("JOB APPLICATION AUTOMATION - Interactive Mode")
    logger.info("%s", "=" * 80)
    
    while True:
        logger.info("Options:")
        logger.info("  1. Process single job posting")
        logger.info("  2. Process multiple job postings")
        logger.info("  3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            url = input("\nEnter Stepstone job URL: ").strip()
            if url:
                process_job_posting(url)
            else:
                logger.error("No URL provided!")
        
        elif choice == '2':
            logger.info("Enter Stepstone URLs (one per line, empty line to finish):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                batch_process_urls(urls)
            else:
                logger.error("No URLs provided!")
        
        elif choice == '3':
            logger.info("Goodbye!")
            break
        
        else:
            logger.error("Invalid option!")


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