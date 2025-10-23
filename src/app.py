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

# Paths configuration
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))
DATA_DIR = Path(get_str('DATA_DIR', 'data'))

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
    """Main page"""
    return render_template('index.html')

@app.route('/batch')
def batch() -> str:
    """Batch processing interface"""
    return render_template('batch.html')

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
    
    # Generate unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize status
    processing_status[job_id] = {
        'status': 'processing',
        'message': 'Starting automation...',
        'url': url,
        'progress': 0
    }
    
    # Process in background thread
    thread = threading.Thread(target=process_in_background, args=(job_id, url))
    thread.start()
    
    return jsonify({'job_id': job_id})

def process_in_background(job_id: str, url: str) -> None:
    """Process job in background"""
    try:
        logger.info(f"[{job_id}] Starting background processing for: {url}")
        processing_status[job_id]['message'] = 'Scraping job posting...'
        processing_status[job_id]['progress'] = 20
        
        result = process_job_posting(url, generate_cover_letter=True, generate_pdf=False)
        logger.info(f"[{job_id}] Process result status: {result.get('status')}")
        
        if result['status'] == 'success':
            def to_str(val):
                return str(val) if isinstance(val, Path) else val
            
            docx_file = result.get('cover_letter_docx_file')
            logger.info(f"[{job_id}] DOCX file created: {docx_file}")
            
            processing_status[job_id] = {
                'status': 'complete',
                'message': 'Automation complete!',
                'progress': 100,
                'result': {
                    'company': result['job_data'].get('company_name'),
                    'title': result['job_data'].get('job_title'),
                    'location': result['job_data'].get('location'),
                    'trello_card': result['trello_card']['shortUrl'],
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
                'progress': 0
            }
    
    except Exception as e:
        logger.exception(f"[{job_id}] Exception in background processing: {e}")
        processing_status[job_id] = {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'progress': 0
        }

@app.route('/status/<job_id>')
def status(job_id: str) -> Response:
    """Get processing status"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_status[job_id])

@app.route('/download/<path:filename>')
def download(filename: str) -> Response:
    """Download generated file"""
    try:
        # Determine correct directory based on file type
        if filename.startswith('scraped_job_'):
            filepath = DATA_DIR / filename
        else:
            filepath = OUTPUT_DIR / filename
        return send_file(str(filepath), as_attachment=True)
    except Exception as e:
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