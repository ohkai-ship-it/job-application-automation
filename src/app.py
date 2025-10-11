"""
Web Interface for Job Application Automation
Simple Flask web app for easy job processing
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from main import process_job_posting
from utils.env import load_env, get_str, validate_env
import threading
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

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
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

def process_in_background(job_id, url):
    """Process job in background"""
    try:
        processing_status[job_id]['message'] = 'Scraping job posting...'
        processing_status[job_id]['progress'] = 20
        
        result = process_job_posting(url, generate_cover_letter=True, generate_pdf=True)
        
        if result['status'] == 'success':
            def to_str(val):
                return str(val) if isinstance(val, Path) else val
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
                        'json': to_str(result['data_file']),
                        'txt': to_str(result.get('cover_letter_text_file')),
                        'docx': to_str(result.get('cover_letter_docx_file')),
                        'pdf': to_str(result.get('cover_letter_pdf_file'))
                    }
                }
            }
        else:
            processing_status[job_id] = {
                'status': 'error',
                'message': f"Error: {result.get('error', 'Unknown error')}",
                'progress': 0
            }
    
    except Exception as e:
        processing_status[job_id] = {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'progress': 0
        }

@app.route('/status/<job_id>')
def status(job_id):
    """Get processing status"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_status[job_id])

@app.route('/download/<path:filename>')
def download(filename):
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

@app.route('/history')
def history():
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

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("JOB APPLICATION AUTOMATION - Web Interface")
    print("=" * 80)
    
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    print(f"\n🌐 Starting web server...")
    print(f"📱 Open your browser and go to: http://{host}:{port}")
    print(f"⚙️  Debug mode: {'enabled' if debug else 'disabled'}")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=debug)
    
    app.run(debug=True, host='0.0.0.0', port=5000)