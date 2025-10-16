"""
LinkedIn Request Monitor

Monitors and logs all LinkedIn-related network requests for analysis.
"""

import json
import time
from datetime import datetime
from pathlib import Path

class LinkedInRequestMonitor:
    def __init__(self):
        self.requests_log = []
        self.rate_limit_warnings = []
        
    def log_request(self, method, url, headers=None, response_status=None):
        """Log a LinkedIn request for analysis"""
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'url': url,
            'headers': headers or {},
            'response_status': response_status,
            'domain': 'linkedin.com' if 'linkedin.com' in url else 'other'
        }
        
        self.requests_log.append(request_data)
        
        # Check for rate limiting indicators
        if response_status and response_status >= 429:
            self.rate_limit_warnings.append(request_data)
            print(f"RATE LIMIT WARNING: {response_status} for {url}")
        
        # Log LinkedIn API requests
        if 'voyager/api' in url:
            print(f"LinkedIn API: {method} {url}")
            
    def save_session_log(self, session_name):
        """Save the current session's requests to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(f"research/linkedin/session_{session_name}_{timestamp}.json")
        
        session_data = {
            'session_name': session_name,
            'timestamp': timestamp,
            'total_requests': len(self.requests_log),
            'linkedin_requests': len([r for r in self.requests_log if 'linkedin.com' in r['url']]),
            'rate_limit_warnings': len(self.rate_limit_warnings),
            'requests': self.requests_log,
            'warnings': self.rate_limit_warnings
        }
        
        with open(log_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"Session log saved: {log_file}")
        return log_file

# Global monitor instance
monitor = LinkedInRequestMonitor()
