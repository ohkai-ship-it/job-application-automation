"""
Main workflow for job application automation.
Scrapes Stepstone job postings, creates Trello cards, generates cover letters, and creates PDFs.
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from scraper import scrape_stepstone_job, save_to_json
from linkedin_scraper import scrape_linkedin_job
from trello_connect import TrelloConnect
from cover_letter import CoverLetterGenerator
from docx_generator import WordCoverLetterGenerator
from database import get_db
from utils.env import load_env, get_str, validate_env
from utils.log_config import get_logger
from utils.error_reporting import report_error
import json
from datetime import datetime
import time

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


def detect_job_source(url: str) -> str:
    """
    Detect whether a URL is from LinkedIn or Stepstone
    
    Args:
        url (str): Job posting URL
        
    Returns:
        str: Either 'linkedin' or 'stepstone'
    """
    url_lower = url.lower()
    
    if 'linkedin.com' in url_lower:
        return 'linkedin'
    elif 'stepstone' in url_lower:
        return 'stepstone'
    else:
        # Default to stepstone for unknown URLs
        logger.warning("Unknown job source for URL: %s (defaulting to stepstone)", url)
        return 'stepstone'

def process_job_posting(
    url: str,
    generate_cover_letter: bool = True,
    generate_pdf: bool = False,  # Disabled by default to save time for manual edits
    skip_duplicate_check: bool = False  # Allow skipping duplicate check for testing
) -> Dict[str, Any]:
    """
    Complete workflow: Scrape job posting, create Trello card, generate cover letter and PDF
    
    Args:
        url (str): Stepstone job posting URL
        generate_cover_letter (bool): Whether to generate a cover letter
        generate_pdf (bool): Whether to convert to PDF (default: False, as manual edits are needed)
        skip_duplicate_check (bool): Skip duplicate detection (for testing/re-processing)
        
    Returns:
        dict: Result with status and data
    """
    
    logger.info("%s", "=" * 80)
    logger.info("JOB APPLICATION AUTOMATION")
    logger.info("%s", "=" * 80)
    logger.info("Processing: %s", url)
    
    # Step 0: Check for duplicates
    # TODO: PRODUCTION - Change this to stop processing on duplicate (return early)
    # For now, we just warn but continue to make testing easier
    if not skip_duplicate_check:
        logger.info("STEP 0: Checking for duplicates...")
        logger.info("%s", "-" * 80)
        
        db = get_db()
        is_duplicate, existing_job = db.check_duplicate(url)
        
        if is_duplicate:
            logger.warning("⚠️  DUPLICATE DETECTED!")
            logger.warning("This job was already processed:")
            logger.warning("  Company: %s", existing_job['company_name'])
            logger.warning("  Job Title: %s", existing_job['job_title'])
            logger.warning("  Processed: %s", existing_job['processed_at'])
            if existing_job.get('trello_card_url'):
                logger.warning("  Trello Card: %s", existing_job['trello_card_url'])
            if existing_job.get('docx_file_path'):
                logger.warning("  Cover Letter: %s", existing_job['docx_file_path'])
            logger.warning("⚠️  CONTINUING ANYWAY (testing mode)")
            logger.warning("⚠️  TODO: In production, this should stop processing!")
            # PRODUCTION: Uncomment the following return statement
            # return {
            #     'status': 'duplicate',
            #     'existing_job': existing_job,
            #     'message': 'Job already processed. Use skip_duplicate_check=True to reprocess.'
            # }
        else:
            logger.info("✓ No duplicate found, proceeding...")
    
    # Step 1: Scrape the job posting
    logger.info("STEP 1: Scraping job posting...")
    logger.info("%s", "-" * 80)
    
    # Detect source and use appropriate scraper
    source = detect_job_source(url)
    logger.info("Detected source: %s", source.upper())
    
    if source == 'linkedin':
        job_data = scrape_linkedin_job(url)
    else:
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
    # Skip saving JSON file
    # filename = DATA_DIR / f"scraped_job_{timestamp}.json"
    # save_to_json(job_data, str(filename))
    
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
            # Check if we should use placeholder (for testing or when OpenAI is unavailable)
            use_placeholder = os.getenv('USE_PLACEHOLDER_COVER_LETTER', 'false').lower() == 'true'
            
            if use_placeholder:
                logger.info("Using placeholder cover letter (OpenAI disabled)")
                
                # We still need the generator for salutation and valediction methods
                # but we'll skip the actual AI call
                try:
                    ai_generator = CoverLetterGenerator()
                except Exception:
                    # If CoverLetterGenerator fails (missing API key), create a minimal mock
                    ai_generator = None
                
                # Generate 200-word placeholder body
                company = job_data.get('company_name', 'the company')
                position = job_data.get('job_title', 'this position')
                placeholder_words = [
                    f"I am writing to express my strong interest in the {position} position at {company}.",
                    "With my extensive background in software development and proven track record of delivering high-quality solutions,",
                    "I am confident that I would be a valuable addition to your team.",
                    "Throughout my career, I have developed expertise in various technologies and methodologies.",
                    "My experience includes working on complex projects that required both technical skills and collaborative teamwork.",
                    "I have consistently demonstrated my ability to adapt to new challenges and learn emerging technologies quickly.",
                    "In my previous roles, I have successfully led development initiatives and mentored junior developers.",
                    "I am particularly drawn to this opportunity because of your company's reputation for innovation and excellence.",
                    "My technical skills combined with my passion for creating elegant solutions make me an ideal candidate.",
                    "I am excited about the possibility of contributing to your team's success and growing with the organization.",
                    "I believe my background aligns well with the requirements outlined in the job description.",
                    "I am eager to bring my expertise to your company and help drive your projects forward.",
                    "Thank you for considering my application. I look forward to the opportunity to discuss",
                    "how my skills can contribute to your team's objectives and organizational goals.",
                ]
                cover_letter_body = " ".join(placeholder_words)
                language = 'english'  # Default to English for placeholder
                
                # Generate salutation and valediction using the generator if available
                if ai_generator:
                    seniority = ai_generator.detect_seniority(
                        job_data.get('job_title', ''),
                        job_data.get('job_description', '')
                    )
                    formality = 'formal'  # Default for placeholder
                    salutation = ai_generator.generate_salutation(job_data, language, formality, seniority)
                    valediction = ai_generator.generate_valediction(language, formality, seniority)
                else:
                    # Fallback if generator not available
                    salutation = "Dear Hiring Manager,"
                    valediction = "Sincerely,"
                    seniority = "mid"
                
                # Store all parts in job_data (same as AI path)
                job_data['cover_letter_salutation'] = salutation
                job_data['cover_letter_body'] = cover_letter_body
                job_data['cover_letter_valediction'] = valediction
                
                # Combine for preview and file saving
                cover_letter_text = f"{salutation}\n\n{cover_letter_body}\n\n{valediction}"
                
                logger.info(f"Generated placeholder: salutation='{salutation}', body_words={len(cover_letter_body.split())}, valediction='{valediction}'")
            else:
                # Generate AI text
                ai_generator = CoverLetterGenerator()
                cover_letter_body = ai_generator.generate_cover_letter(job_data)
                
                # Detect language
                language = ai_generator.detect_language(job_data.get('job_description', ''))
                
                # Combine salutation + body + valediction for complete letter
                salutation = job_data.get('cover_letter_salutation', '')
                valediction = job_data.get('cover_letter_valediction', '')
                cover_letter_text = f"{salutation}\n\n{cover_letter_body}\n\n{valediction}"
            
            # Display preview
            logger.info("--- Cover Letter Preview ---")
            preview = cover_letter_text[:300] + "..." if len(cover_letter_text) > 300 else cover_letter_text
            logger.info("%s", preview)
            logger.info("%s", "-" * 80)
            
            # Save text version (complete with salutation and valediction)
            if use_placeholder:
                # Skip saving TXT file for placeholder
                # output_dir = Path('output/cover_letters')
                # output_dir.mkdir(parents=True, exist_ok=True)
                # company_safe = job_data.get('company_name', 'Company').replace(' ', '_')
                # timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
                # cover_letter_file = output_dir / f"cover_letter_{company_safe}_{timestamp_now}.txt"
                # with open(cover_letter_file, 'w', encoding='utf-8') as f:
                #     f.write(cover_letter_text)
                # logger.info(f"Cover letter saved: {cover_letter_file}")
                logger.info("TXT file generation skipped (not needed)")
            else:
                # Skip saving TXT file for AI path too
                # output_dir = Path('output/cover_letters')
                # output_dir.mkdir(parents=True, exist_ok=True)
                # company_safe = job_data.get('company_name', 'Company').replace(' ', '_')
                # timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
                # cover_letter_file = output_dir / f"cover_letter_{company_safe}_{timestamp_now}.txt"
                # with open(cover_letter_file, 'w', encoding='utf-8') as f:
                #     f.write(cover_letter_text)
                # logger.info(f"Cover letter saved: {cover_letter_file}")
                logger.info("TXT file generation skipped (not needed)")
            
            # Step 4: Generate Word document
            logger.info("%s", "=" * 80)
            logger.info("STEP 4: Creating Word document...")
            logger.info("%s", "-" * 80)
            
            word_generator = WordCoverLetterGenerator()
            
            # Generate filename based on language
            sender_name = word_generator.sender['name']  # "Dr. Kai Voges"
            # Remove title (Dr., Prof., etc.) from filename
            sender_name_no_title = sender_name.replace('Dr. ', '').replace('Prof. ', '')
            company_name = job_data.get('company_name', 'Company')
            date_str = datetime.now().strftime('%Y-%m-%d')  # e.g., "2025-10-14"
            
            if language == 'german':
                base_filename = f"Anschreiben - {sender_name_no_title} - {date_str} - {company_name}"
            else:  # English
                base_filename = f"Cover letter - {sender_name_no_title} - {date_str} - {company_name}"
            
            docx_filename = f"output/cover_letters/{base_filename}.docx"
            
            # Important: Pass only the BODY to the template generator
            # The template has separate placeholders for salutation and valediction
            cover_letter_body_only = job_data.get('cover_letter_body', cover_letter_text)
            
            docx_file = word_generator.generate_from_template(
                cover_letter_body_only,
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
    
    # Save to database (after successful processing)
    # In testing mode, we skip saving if it's a duplicate to avoid UNIQUE constraint errors
    if not skip_duplicate_check:
        logger.info("%s", "=" * 80)
        logger.info("Saving to database...")
        logger.info("%s", "-" * 80)
        
        try:
            db = get_db()
            
            # Check if this is a duplicate before trying to save
            is_duplicate, _ = db.check_duplicate(url)
            
            if is_duplicate:
                logger.info("⚠️  Skipping database save - job already exists in database")
                logger.info("    (This is expected in testing mode when processing duplicates)")
            else:
                # Extract AI metadata if available
                ai_model = job_data.get('ai_model_used', 'gpt-4o-mini')
                language_code = job_data.get('detected_language', 'de')
                word_count = job_data.get('cover_letter_word_count', None)
                generation_cost = job_data.get('ai_generation_cost', None)
                
                job_id = db.save_processed_job(
                    source_url=url,
                    company_name=job_data.get('company_name', 'Unknown'),
                    job_title=job_data.get('job_title', 'Unknown'),
                    trello_card_id=card.get('id'),
                    trello_card_url=card.get('shortUrl'),
                    docx_file_path=str(docx_file) if docx_file else None,
                    ai_model=ai_model if generate_cover_letter else None,
                    language=language_code if generate_cover_letter else None,
                    word_count=word_count,
                    generation_cost=generation_cost,
                    cover_letter_text=cover_letter_text if generate_cover_letter else None
                )
                
                logger.info("✓ Saved to database (job_id: %s)", job_id)
            
        except Exception as e:
            logger.warning("Failed to save to database: %s", e)
            # Non-critical error, continue anyway
    
    # Success!
    logger.info("%s", "=" * 80)
    logger.info("AUTOMATION COMPLETE!")
    logger.info("%s", "=" * 80)

    logger.info("Summary:")
    logger.info("  Company: %s", job_data.get('company_name', 'N/A'))
    logger.info("  Position: %s", job_data.get('job_title', 'N/A'))
    logger.info("  Location: %s", job_data.get('location', 'N/A'))
    logger.info("  Trello Card: %s", card['shortUrl'])
    # logger.info("  Data saved: %s", filename)  # JSON file saving disabled
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
        # 'data_file': filename,  # JSON file saving disabled
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
            url = input("\nEnter job URL (Stepstone or LinkedIn): ").strip()
            if url:
                process_job_posting(url)
            else:
                logger.error("No URL provided!")
        
        elif choice == '2':
            logger.info("Enter job URLs (Stepstone or LinkedIn, one per line, empty line to finish):")
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