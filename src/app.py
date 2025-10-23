"""
Web Interface for Job Application Automation
Simple Flask web app for easy job processing
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.exceptions import HTTPException
import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from main import process_job_posting
from database import get_db
from utils.env import load_env, get_str, validate_env
from utils.log_config import get_logger
from utils.error_reporting import report_error
import threading
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

# Flask configuration
app = Flask(__name__, template_folder='../templates')
app.config.update(
    HOST=get_str('FLASK_HOST', '127.0.0.1'),
    PORT=int(get_str('FLASK_PORT', '5000')),
    DEBUG=get_str('FLASK_DEBUG', 'False').lower() == 'true'
)

# Paths configuration (relative to project root, not src/)
APP_ROOT = Path(__file__).parent.parent  # Go up from src/ to project root

# Get paths from env or use defaults relative to project root
output_dir_env = get_str('OUTPUT_DIR', '').strip()
data_dir_env = get_str('DATA_DIR', '').strip()

OUTPUT_DIR = Path(output_dir_env) if output_dir_env else (APP_ROOT / 'output')
DATA_DIR = Path(data_dir_env) if data_dir_env else (APP_ROOT / 'data')

# Store processing status
processing_status = {}


@app.errorhandler(Exception)
def handle_exception(e: Exception):
    """Global error handler returning JSON and recording unexpected errors.

    - 404/HTTPExceptions are returned without recording as errors (404 is common for /favicon.ico)
    - Other HTTPExceptions are recorded with severity=warning
    - Non-HTTP exceptions are recorded with severity=error
    """
    # Handle known HTTP exceptions gracefully
    if isinstance(e, HTTPException):
        status = e.code or 500
        # Do not report 404s as errors (browsers commonly request /favicon.ico)
        if status == 404:
            logger.info("Route not found: %s %s", getattr(request, 'method', '?'), getattr(request, 'path', '?'))
            return jsonify({"error": "Not Found", "path": getattr(request, 'path', None)}), 404

        # For other HTTP exceptions, record as warning
        try:
            report_error(
                "HTTPException in Flask app",
                exc=e,
                context={
                    "path": getattr(request, 'path', None),
                    "method": getattr(request, 'method', None),
                    "status": status,
                },
                severity="warning",
            )
        finally:
            logger.warning("HTTPException: %s", e)
        return jsonify({"error": e.name, "message": e.description}), status

    # Non-HTTP exceptions: unexpected errors
    try:
        report_error(
            "Unhandled exception in Flask app",
            exc=e,
            context={
                "path": getattr(request, 'path', None),
                "method": getattr(request, 'method', None),
            },
            severity="error",
        )
    finally:
        logger.exception("Unhandled exception: %s", e)
    return jsonify({"error": str(e)}), 500

@app.route('/')
def index() -> str:
    """Main page - redirect to batch processor"""
    return render_template('batch.html')

@app.route('/batch')
def batch() -> str:
    """Batch processing interface"""
    return render_template('batch.html')

@app.route('/classic')
def classic() -> str:
    """Classic single-URL processor (legacy)"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon() -> Response:
    """Prevent noisy 404s from browser favicon requests."""
    return Response(status=204)

@app.route('/process', methods=['POST'])
def process() -> Response:
    """Process a job URL"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Get settings from request
    create_trello_card = data.get('create_trello_card', False)
    generate_documents = data.get('generate_documents', False)
    generate_pdf = data.get('generate_pdf', False)
    target_language = data.get('target_language', 'auto')  # NEW: Target language (auto, de, en)
    
    # Validation: At least one option must be selected
    if not create_trello_card and not generate_documents:
        return jsonify({
            'error': 'At least one of "Create Trello Card" or "Generate Documents" must be selected'
        }), 400
    
    # PDF only makes sense if generating documents
    if generate_pdf and not generate_documents:
        generate_pdf = False  # Silently ignore orphaned PDF flag
    
    # Generate unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize status
    processing_status[job_id] = {
        'status': 'processing',
        'message': 'Starting automation...',
        'url': url,
        'progress': 0,
        'job_title': '',  # Will be populated after early scrape
        'company_name': '',  # Will be populated after early scrape
        'source_url': None,  # Will be populated after early scrape
        'company_page_url': None,  # Will be populated after early scrape
        'paused': False  # Pause flag
    }
    
    # Process in background thread with settings
    thread = threading.Thread(
        target=process_in_background,
        args=(job_id, url, create_trello_card, generate_documents, generate_pdf, target_language)
    )
    thread.start()
    
    return jsonify({'job_id': job_id})

def process_in_background(
    job_id: str,
    url: str,
    create_trello_card: bool = True,
    generate_documents: bool = True,
    generate_pdf: bool = False,
    target_language: str = 'auto'  # NEW: Target language (auto, de, en)
) -> None:
    """Process job in background with real-time progress updates"""
    try:
        logger.info(f"[{job_id}] Starting background processing for: {url}")
        logger.info(f"[{job_id}] Settings: create_trello_card={create_trello_card}, generate_pdf={generate_pdf}")
        
        # Initialize progress
        processing_status[job_id]['message'] = 'Gathering Information'
        processing_status[job_id]['progress'] = 5
        
        # Step 1: Do quick scrape BEFORE starting the blocking process_job_posting call
        # This gives frontend time to grab the data during early aggressive polling
        logger.info(f"[{job_id}] Quick scrape to extract job info...")
        try:
            from main import detect_job_source, scrape_job_posting
            
            source = detect_job_source(url)
            job_data = scrape_job_posting(url)
            
            if job_data:
                # Set the fields immediately - frontend will poll and catch them
                processing_status[job_id]['job_title'] = job_data.get('job_title', 'Unknown')
                processing_status[job_id]['company_name'] = job_data.get('company_name', 'Unknown')
                processing_status[job_id]['source_url'] = job_data.get('source_url')
                processing_status[job_id]['company_page_url'] = job_data.get('company_page_url')
                logger.info(f"[{job_id}] Job info extracted: {processing_status[job_id]['company_name']} - {processing_status[job_id]['job_title']}")
                logger.info(f"[{job_id}] URLs - JD: {processing_status[job_id]['source_url']}, Company: {processing_status[job_id]['company_page_url']}")
            else:
                logger.warning(f"[{job_id}] Quick scrape returned no data")
        except Exception as e:
            logger.warning(f"[{job_id}] Quick scrape failed: {e}")
        
        # Check if job was cancelled while we were scraping
        if job_id not in processing_status:
            logger.warning(f"[{job_id}] Job was cancelled, skipping processing")
            return
        
        processing_status[job_id]['progress'] = 15
        
        # Create progress callback that will POST updates to the frontend
        def progress_callback(progress=0, message='', job_title='', company_name=''):
            """Callback to report real progress from main.py to frontend"""
            try:
                # Check if job still exists (might have been cancelled)
                if job_id not in processing_status:
                    logger.debug(f"[{job_id}] Job no longer in processing_status, skipping progress update")
                    return
                
                processing_status[job_id]['progress'] = progress
                if message:
                    processing_status[job_id]['message'] = message
                if job_title:
                    processing_status[job_id]['job_title'] = job_title
                if company_name:
                    processing_status[job_id]['company_name'] = company_name
                logger.debug(f"[{job_id}] Progress: {progress}% - {message}")
            except Exception as e:
                logger.warning(f"[{job_id}] Error in progress callback: {e}")
        
        # NOW process the job with the specified settings
        result = process_job_posting(
            url,
            generate_cover_letter=generate_documents,
            generate_pdf=generate_pdf,
            create_trello_card=create_trello_card,
            target_language=target_language,
            progress_callback=progress_callback  # NEW: Pass callback
        )
        logger.info(f"[{job_id}] Process result status: {result.get('status')}")
        
        # Check if job was cancelled while processing
        if job_id not in processing_status or processing_status[job_id].get('status') == 'cancelled':
            logger.warning(f"[{job_id}] Job was cancelled during processing, not updating status")
            return
        
        if result['status'] == 'success':
            
            def to_str(val):
                return str(val) if isinstance(val, Path) else val
            
            docx_file = result.get('cover_letter_docx_file')
            logger.info(f"[{job_id}] DOCX file created: {docx_file}")
            
            # Step 5: Complete
            trello_card_url = None
            if result.get('trello_card'):
                trello_card_url = result['trello_card']['shortUrl']
            
            processing_status[job_id] = {
                'status': 'complete',
                'message': 'Automation complete!',
                'progress': 100,
                'url': processing_status[job_id].get('url'),
                'result': {
                    'company': result['job_data'].get('company_name'),
                    'title': result['job_data'].get('job_title'),
                    'location': result['job_data'].get('location'),
                    'source_url': result['job_data'].get('source_url'),
                    'company_page_url': result['job_data'].get('company_page_url'),
                    'trello_card': trello_card_url,
                    'is_duplicate': result.get('is_duplicate', False),  # NEW: Flag indicating duplicate
                    'files': {
                        # 'json': to_str(result.get('data_file')),  # JSON file generation disabled
                        # 'txt': to_str(result.get('cover_letter_text_file')),  # TXT file generation disabled
                        'docx': to_str(docx_file),
                        'pdf': to_str(result.get('cover_letter_pdf_file'))
                    }
                }
            }
            logger.info(f"[{job_id}] Processing complete successfully")
        elif result['status'] == 'cover_letter_failed':
            # NEW: Handle cover letter generation failure (allow retry)
            logger.warning(f"[{job_id}] Processing complete but cover letter generation failed: {result.get('cover_letter_error')}")
            trello_card_url = None
            if result.get('trello_card'):
                trello_card_url = result['trello_card']['shortUrl']
            
            processing_status[job_id] = {
                'status': 'cover_letter_failed',
                'message': f"Cover letter failed: {result.get('cover_letter_error')}",
                'progress': 100,
                'url': processing_status[job_id].get('url'),
                'job_data': result.get('job_data'),  # Store for retry
                'result': {
                    'company': result['job_data'].get('company_name'),
                    'title': result['job_data'].get('job_title'),
                    'location': result['job_data'].get('location'),
                    'source_url': result['job_data'].get('source_url'),
                    'company_page_url': result['job_data'].get('company_page_url'),
                    'trello_card': trello_card_url,
                    'is_duplicate': result.get('is_duplicate', False),
                    'files': {
                        'docx': None,
                        'pdf': None
                    }
                }
            }
        else:
            logger.error(f"[{job_id}] Processing failed: {result.get('error')}")
            processing_status[job_id] = {
                'status': 'error',
                'message': f"Error: {result.get('error', 'Unknown error')}",
                'progress': 100
            }
    
    except Exception as e:
        logger.exception(f"[{job_id}] Exception in background processing: {e}")
        processing_status[job_id] = {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'progress': 100
        }

@app.route('/status/<job_id>')
def status(job_id: str) -> Response:
    """Get processing status"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    status_data = processing_status[job_id]
    logger.debug(f"[{job_id}] Status response: source_url={status_data.get('source_url')}, company_page_url={status_data.get('company_page_url')}")
    return jsonify(status_data)

@app.route('/update-progress/<job_id>', methods=['POST'])
def update_progress(job_id: str) -> Response:
    """Update job progress from backend processing (main.py)"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    data = request.json or {}
    
    # Update progress fields
    if 'progress' in data:
        processing_status[job_id]['progress'] = int(data['progress'])
    if 'message' in data:
        processing_status[job_id]['message'] = str(data['message'])
    if 'job_title' in data:
        processing_status[job_id]['job_title'] = str(data['job_title'])
    if 'company_name' in data:
        processing_status[job_id]['company_name'] = str(data['company_name'])
    
    logger.debug(f"[{job_id}] Progress updated: {data}")
    return jsonify({'success': True, 'status': processing_status[job_id]['status']})

@app.route('/pause/<job_id>', methods=['POST'])
def pause_job(job_id: str) -> Response:
    """Pause or resume a job"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    # Toggle pause state
    processing_status[job_id]['paused'] = not processing_status[job_id].get('paused', False)
    is_paused = processing_status[job_id]['paused']
    
    if is_paused:
        processing_status[job_id]['message'] = 'Paused'
    else:
        processing_status[job_id]['message'] = 'Resuming...'
    
    logger.info(f"[{job_id}] Job {'paused' if is_paused else 'resumed'}")
    return jsonify({'paused': is_paused})

@app.route('/cancel', methods=['POST'])
def cancel_all() -> Response:
    """Cancel all jobs and mark them as cancelled (don't delete from processing_status)"""
    try:
        # Mark all processing/queued jobs as cancelled instead of clearing them
        # This allows them to be deleted later
        for job_id, job_status in list(processing_status.items()):
            if job_status['status'] in ['processing', 'queued']:
                logger.info(f"[{job_id}] Marking job as cancelled")
                processing_status[job_id]['status'] = 'cancelled'
                processing_status[job_id]['message'] = 'Job cancelled by user'
        
        logger.info("All jobs marked as cancelled")
        return jsonify({'success': True, 'message': 'All jobs cancelled'})
    except Exception as e:
        logger.exception("Error cancelling jobs: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/retry-cover-letter/<job_id>', methods=['POST'])
def retry_cover_letter(job_id: str) -> Response:
    """Retry cover letter generation for a failed job"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    status_info = processing_status[job_id]
    if status_info['status'] != 'cover_letter_failed':
        return jsonify({'error': 'Job must have cover_letter_failed status to retry'}), 400
    
    # Get the job data from processing status
    job_data = status_info.get('job_data')
    if not job_data:
        return jsonify({'error': 'Job data not found for retry'}), 400
    
    # Reset status and start retry in background
    processing_status[job_id]['status'] = 'processing'
    processing_status[job_id]['progress'] = 60  # Start at AI phase
    processing_status[job_id]['message'] = 'Generating Cover Letter with AI (Retry)'
    
    def retry_in_background():
        try:
            from cover_letter import CoverLetterGenerator
            
            logger.info(f"[{job_id}] Retrying cover letter generation...")
            
            # Re-generate cover letter
            ai_generator = CoverLetterGenerator()
            cover_letter_body = ai_generator.generate_cover_letter(job_data)
            
            if not cover_letter_body:
                processing_status[job_id]['status'] = 'cover_letter_failed'
                processing_status[job_id]['message'] = 'Cover letter generation failed (still too short)'
                logger.warning(f"[{job_id}] Retry failed: No cover letter generated")
                return
            
            # Store in job_data for document generation
            job_data['cover_letter_body'] = cover_letter_body
            
            # Generate Word document
            processing_status[job_id]['progress'] = 80
            processing_status[job_id]['message'] = 'Creating Word document'
            
            from docx_generator import WordCoverLetterGenerator
            word_generator = WordCoverLetterGenerator()
            
            # Detect language
            language = ai_generator.detect_language(job_data.get('job_description', ''))
            
            # Generate filename
            sender_name = word_generator.sender['name']
            sender_name_no_title = sender_name.replace('Dr. ', '').replace('Prof. ', '')
            company_name = job_data.get('company_name', 'Company')
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if language == 'german':
                base_filename = f"Anschreiben - {sender_name_no_title} - {date_str} - {company_name}"
            else:
                base_filename = f"Cover letter - {sender_name_no_title} - {date_str} - {company_name}"
            
            docx_filename = f"output/cover_letters/{base_filename}.docx"
            docx_file = word_generator.generate_from_template(
                cover_letter_body,
                job_data,
                docx_filename,
                language=language
            )
            
            # Success!
            processing_status[job_id]['status'] = 'complete'
            processing_status[job_id]['progress'] = 100
            processing_status[job_id]['message'] = 'Cover letter generated successfully!'
            processing_status[job_id]['result'] = {
                'company': job_data.get('company_name'),
                'title': job_data.get('job_title'),
                'location': job_data.get('location'),
                'source_url': job_data.get('source_url'),
                'company_page_url': job_data.get('company_page_url'),
                'trello_card': status_info.get('result', {}).get('trello_card'),
                'is_duplicate': job_data.get('is_duplicate', False),
                'files': {
                    'docx': str(docx_file),
                    'pdf': None
                }
            }
            logger.info(f"[{job_id}] Cover letter retry successful!")
            
        except Exception as e:
            logger.exception(f"[{job_id}] Cover letter retry failed: {e}")
            processing_status[job_id]['status'] = 'cover_letter_failed'
            processing_status[job_id]['message'] = f'Retry failed: {str(e)}'
            processing_status[job_id]['progress'] = 100
    
    import threading
    retry_thread = threading.Thread(target=retry_in_background, daemon=True)
    retry_thread.start()
    
    return jsonify({'success': True, 'message': 'Cover letter retry started'})


@app.route('/delete/<job_id>', methods=['POST'])
def delete_job(job_id: str) -> Response:
    """Delete a job, its files, and Trello card"""
    try:
        from src.file_manager import delete_generated_files
        from src.trello_connect import TrelloConnect
        from src.database import ApplicationDB
        
        # Get job info
        job_info = processing_status.get(job_id, {})
        result = job_info.get('result', {})
        
        deleted = {
            'trello_card': False,
            'docx': False,
            'pdf': False,
            'database': False
        }
        
        # 1. Delete Trello card
        trello_card_url = result.get('trello_card')
        if trello_card_url:
            try:
                # Extract card ID from URL: https://trello.com/c/CARD_ID
                card_id = trello_card_url.split('/c/')[-1] if '/c/' in trello_card_url else None
                if card_id:
                    trello = TrelloConnect()
                    deleted['trello_card'] = trello.delete_card(card_id)
            except Exception as e:
                logger.error(f"[{job_id}] Error deleting Trello card: {e}")
        
        # 2. Delete generated files
        files = result.get('files', {})
        file_results = delete_generated_files(
            docx_file=files.get('docx'),
            pdf_file=files.get('pdf')
        )
        deleted['docx'] = file_results.get('docx', False)
        deleted['pdf'] = file_results.get('pdf', False)
        
        # 3. Delete database record
        try:
            db = ApplicationDB()
            # Get source_url from result or job_info (for in-progress jobs)
            source_url = result.get('source_url') or job_info.get('url')
            
            # Try to delete by job_id first
            deleted['database'] = db.delete_job(job_id=job_id)
            
            # If first delete didn't work, try by source_url as fallback
            if not deleted['database'] and source_url:
                deleted['database'] = db.delete_job(source_url=source_url)
                logger.info(f"[{job_id}] Deleted by source_url fallback: {source_url}")
        except Exception as e:
            logger.error(f"[{job_id}] Error deleting from database: {e}")
        
        # 4. Remove from processing_status
        if job_id in processing_status:
            del processing_status[job_id]
        
        logger.info(f"[{job_id}] Job deleted successfully. Trello: {deleted['trello_card']}, "
                   f"DOCX: {deleted['docx']}, PDF: {deleted['pdf']}, DB: {deleted['database']}")
        
        return jsonify({
            'success': True,
            'deleted': deleted,
            'message': 'Job deleted successfully'
        })
    
    except Exception as e:
        logger.error(f"[{job_id}] Error deleting job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download/<path:filename>')
def download(filename: str) -> Response:
    """Download generated file"""
    try:
        import os
        
        # Extract just the filename from the path
        # Example: "output/cover_letters/file.docx" → "file.docx"
        just_filename = os.path.basename(filename)
        logger.info(f"Download request: filename={filename}, basename={just_filename}")
        
        # Determine directory and filepath
        if filename.startswith('scraped_job_'):
            filepath = DATA_DIR / just_filename
            logger.info(f"  Looking in DATA_DIR: {filepath}")
        else:
            # Most files are in output/cover_letters
            filepath = OUTPUT_DIR / 'cover_letters' / just_filename
            logger.info(f"  Looking in cover_letters: {filepath}")
        
        # Verify file exists before attempting download
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return jsonify({'error': f'File not found: {just_filename}'}), 404
        
        logger.info(f"  Sending file: {filepath}")
        return send_file(
            str(filepath), 
            as_attachment=True,
            download_name=just_filename
        )
    except Exception as e:
        logger.exception(f"Download error for {filename}: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/recent-files')
def get_recent_files() -> Response:
    """Get recently generated output files (cover letters, DOCX, PDF, etc.)
    
    Query params:
      - limit: int (default 10, max 50)
    """
    try:
        limit_str = request.args.get('limit', '10')
        try:
            limit = max(1, min(50, int(limit_str)))
        except ValueError:
            limit = 10

        files = []
        
        # Get cover letters (TXT files)
        cover_letters_dir = OUTPUT_DIR / 'cover_letters'
        if cover_letters_dir.exists():
            for filepath in cover_letters_dir.glob('*.txt'):
                if not filepath.name.startswith('.'):
                    try:
                        stat = filepath.stat()
                        files.append({
                            'name': filepath.name,
                            'type': 'cover_letter',
                            'path': f'cover_letters/{filepath.name}',
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })
                    except Exception:
                        pass
        
        # Get DOCX files
        if (OUTPUT_DIR / 'cover_letters').exists():
            for filepath in (OUTPUT_DIR / 'cover_letters').glob('*.docx'):
                if not filepath.name.startswith('.'):
                    try:
                        stat = filepath.stat()
                        files.append({
                            'name': filepath.name,
                            'type': 'docx',
                            'path': f'cover_letters/{filepath.name}',
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })
                    except Exception:
                        pass
        
        # Get PDF files
        if (OUTPUT_DIR / 'cover_letters').exists():
            for filepath in (OUTPUT_DIR / 'cover_letters').glob('*.pdf'):
                if not filepath.name.startswith('.'):
                    try:
                        stat = filepath.stat()
                        files.append({
                            'name': filepath.name,
                            'type': 'pdf',
                            'path': f'cover_letters/{filepath.name}',
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })
                    except Exception:
                        pass

        # Sort by modification time, most recent first
        files.sort(key=lambda f: f['modified'], reverse=True)
        
        return jsonify({'files': files[:limit]})
    except Exception as e:
        logger.exception("Error loading recent files")
        return jsonify({'files': []})

@app.route('/history')
def history() -> Response:
    """Get processing history"""
    # Sort by most recent first
    jobs = []
    for job_id, data in sorted(processing_status.items(), reverse=True):
        jobs.append({
            'id': job_id,
            'status': data['status'],
            'url': data.get('url', ''),
            'company': data.get('result', {}).get('company', 'N/A') if data['status'] == 'complete' else 'N/A',
            'title': data.get('result', {}).get('title', 'N/A') if data['status'] == 'complete' else 'N/A'
        })
    
    return jsonify({'jobs': jobs})


@app.get('/errors')
def list_errors() -> Response:
    """List recent error reports from output/errors.

    Query params:
      - limit: int (default 20, max 200)
    """
    try:
        limit_str = request.args.get('limit', '20')
        try:
            limit = max(1, min(200, int(limit_str)))
        except ValueError:
            limit = 20

        errors_dir = OUTPUT_DIR / 'errors'
        if not errors_dir.exists():
            return jsonify({'errors': []})

        # Load and sort by timestamp in JSON (fallback to filename timestamp or mtime)
        items = []
        for p in errors_dir.glob('error_*.json'):
            try:
                raw = p.read_text('utf-8')
                data = json.loads(raw)
                ts = data.get('timestamp')
                if not ts:
                    name = p.name
                    if name.startswith('error_') and name.endswith('.json'):
                        ts = name[len('error_'):-len('.json')]
                items.append((ts or '', p.stat().st_mtime, data, p))
            except Exception:
                continue

        items.sort(key=lambda t: (t[0], t[1]), reverse=True)
        results = []
        for ts, _mtime, data, p in items[:limit]:
            results.append({
                'id': data.get('id'),
                'timestamp': data.get('timestamp') or ts,
                'severity': data.get('severity'),
                'message': data.get('message'),
                'file': str(p.relative_to(OUTPUT_DIR)) if p.exists() else str(p),
            })
        return jsonify({'errors': results})
    except Exception as e:
        # Let global handler capture details; return generic response
        raise e

@app.get('/outputs')
def list_outputs() -> Response:
    """List all output files (cover letters, PDFs, etc.)"""
    try:
        files = []
        
        # Get cover letters
        cover_letters_dir = OUTPUT_DIR / 'cover_letters'
        if cover_letters_dir.exists():
            for f in sorted(cover_letters_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
                if f.is_file():
                    files.append({
                        'name': f.name,
                        'type': 'cover_letter',
                        'path': str(f.relative_to(OUTPUT_DIR)),
                        'timestamp': f.stat().st_mtime,
                        'size': f.stat().st_size,
                    })
        
        return jsonify({'files': files})
    except Exception as e:
        logger.exception("Error listing outputs: %s", e)
        return jsonify({'files': []})

@app.get('/api/recent-files')
def api_recent_files() -> Response:
    """API endpoint: Get recent generated files (for batch UI)"""
    try:
        limit = min(100, int(request.args.get('limit', 10)))
        files = []
        
        cover_letters_dir = OUTPUT_DIR / 'cover_letters'
        if cover_letters_dir.exists():
            for f in sorted(cover_letters_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
                if f.is_file():
                    files.append({
                        'name': f.name,
                        'path': f'cover_letters/{f.name}',
                        'time': f.stat().st_mtime,
                        'type': 'docx' if f.suffix == '.docx' else 'pdf' if f.suffix == '.pdf' else 'other'
                    })
        
        return jsonify({'files': files})
    except Exception as e:
        logger.exception("Error getting recent files: %s", e)
        return jsonify({'files': []})

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logger.info("%s", "=" * 80)
    logger.info("JOB APPLICATION AUTOMATION - Web Interface")
    logger.info("%s", "=" * 80)
    
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    logger.info("Starting web server...")
    base_url = f"http://{host}:{port}"
    logger.info("Open your browser and go to:")
    logger.info("  Single Job Processing: %s/", base_url)
    logger.info("  Batch Processing:      %s/batch", base_url)
    logger.info("Debug mode: %s", 'enabled' if debug else 'disabled')
    logger.info("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)