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
    """Batch processor page"""
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
    create_trello_card = data.get('create_trello_card', True)
    generate_pdf = data.get('generate_pdf', False)
    
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
        'paused': False  # Pause flag
    }
    
    # Process in background thread with settings
    thread = threading.Thread(target=process_in_background, args=(job_id, url, create_trello_card, generate_pdf))
    thread.start()
    
    return jsonify({'job_id': job_id})

def process_in_background(job_id: str, url: str, create_trello_card: bool = True, generate_pdf: bool = False) -> None:
    """Process job in background with real-time progress updates"""
    try:
        logger.info(f"[{job_id}] Starting background processing for: {url}")
        logger.info(f"[{job_id}] Settings: create_trello_card={create_trello_card}, generate_pdf={generate_pdf}")
        
        # Initialize progress
        processing_status[job_id]['message'] = 'Gathering information...'
        processing_status[job_id]['progress'] = 5
        
        # Step 1: Do quick scrape BEFORE starting the blocking process_job_posting call
        # This gives frontend time to grab the data during early aggressive polling
        logger.info(f"[{job_id}] Quick scrape to extract job info...")
        try:
            from src.scraper import detect_job_source, scrape_stepstone_job
            from src.linkedin_scraper import scrape_linkedin_job as scrape_linkedin
            
            source = detect_job_source(url)
            job_data = scrape_linkedin(url) if source == 'linkedin' else scrape_stepstone_job(url)
            
            if job_data:
                # Set the fields immediately - frontend will poll and catch them
                processing_status[job_id]['job_title'] = job_data.get('job_title', 'Unknown')
                processing_status[job_id]['company_name'] = job_data.get('company_name', 'Unknown')
                logger.info(f"[{job_id}] Job info extracted: {processing_status[job_id]['company_name']} - {processing_status[job_id]['job_title']}")
        except Exception as e:
            logger.warning(f"[{job_id}] Quick scrape failed: {e}")
        
        processing_status[job_id]['progress'] = 15
        
        # Step 2: Update message and progress for Trello phase
        processing_status[job_id]['message'] = 'Logging in Trello...'
        processing_status[job_id]['progress'] = 20
        
        # Animate progress during the blocking process_job_posting call
        import threading
        
        def animate_progress():
            """Animate progress updates during blocking processing"""
            # Simulate progress from 25% to 59% during Trello phase
            for p in range(25, 60, 5):
                time.sleep(0.3)
                # Check pause flag frequently
                while processing_status[job_id].get('paused', False):
                    time.sleep(0.1)
                if processing_status[job_id]['progress'] < 60:
                    processing_status[job_id]['progress'] = p
            
            # Simulate cover letter phase (60-79%)
            time.sleep(0.1)
            while processing_status[job_id].get('paused', False):
                time.sleep(0.1)
            if processing_status[job_id]['progress'] < 80:
                processing_status[job_id]['message'] = 'Generating cover letter...'
                processing_status[job_id]['progress'] = 60
            
            for p in range(65, 80, 5):
                time.sleep(0.3)
                # Check pause flag frequently
                while processing_status[job_id].get('paused', False):
                    time.sleep(0.1)
                if processing_status[job_id]['progress'] < 80:
                    processing_status[job_id]['progress'] = p
            
            # Simulate document phase (80-99%)
            time.sleep(0.1)
            while processing_status[job_id].get('paused', False):
                time.sleep(0.1)
            if processing_status[job_id]['progress'] < 100:
                processing_status[job_id]['message'] = 'Creating documents...'
                processing_status[job_id]['progress'] = 80
            
            for p in range(85, 100, 5):
                time.sleep(0.3)
                # Check pause flag frequently
                while processing_status[job_id].get('paused', False):
                    time.sleep(0.1)
                if processing_status[job_id]['progress'] < 100:
                    processing_status[job_id]['progress'] = p
        
        # Start progress animation in background
        animator = threading.Thread(target=animate_progress, daemon=True)
        animator.start()
        
        # NOW process the job with the specified settings
        result = process_job_posting(url, generate_cover_letter=True, generate_pdf=generate_pdf, create_trello_card=create_trello_card)
        logger.info(f"[{job_id}] Process result status: {result.get('status')}")
        
        # Wait for animator to finish
        time.sleep(0.5)
        
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
                'result': {
                    'company': result['job_data'].get('company_name'),
                    'title': result['job_data'].get('job_title'),
                    'location': result['job_data'].get('location'),
                    'trello_card': trello_card_url,
                    'files': {
                        # 'json': to_str(result.get('data_file')),  # JSON file generation disabled
                        # 'txt': to_str(result.get('cover_letter_text_file')),  # TXT file generation disabled
                        'docx': to_str(docx_file),
                        'pdf': to_str(result.get('cover_letter_pdf_file'))
                    }
                }
            }
            logger.info(f"[{job_id}] Processing complete successfully")
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
    
    return jsonify(processing_status[job_id])

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
    """Cancel all jobs and clean up database"""
    try:
        # Clear all processing status entries
        processing_status.clear()
        
        # Clear database
        db = get_db()
        db.clear_all()
        
        logger.info("All jobs cancelled and database cleaned")
        return jsonify({'success': True, 'message': 'All jobs cancelled and database cleaned'})
    except Exception as e:
        logger.exception("Error cancelling jobs: %s", e)
        return jsonify({'error': str(e)}), 500

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
    logger.info("Open your browser and go to: http://%s:%s", host, port)
    logger.info("Debug mode: %s", 'enabled' if debug else 'disabled')
    logger.info("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)