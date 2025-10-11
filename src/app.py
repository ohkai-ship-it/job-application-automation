"""
Web Interface for Job Application Automation
Simple Flask web app for easy job processing
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import process_job_posting
import threading
import json
from datetime import datetime

app = Flask(__name__, template_folder='../templates')

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
                        'json': result['data_file'],
                        'txt': result.get('cover_letter_text_file'),
                        'docx': result.get('cover_letter_docx_file'),
                        'pdf': result.get('cover_letter_pdf_file')
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
        return send_file(filename, as_attachment=True)
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
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "=" * 80)
    print("JOB APPLICATION AUTOMATION - Web Interface")
    print("=" * 80)
    print("\n🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)