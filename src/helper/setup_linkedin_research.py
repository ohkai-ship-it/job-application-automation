"""
LinkedIn Research Environment Setup

This script helps set up an isolated environment for LinkedIn integration research.
It creates browser profiles, installs necessary tools, and sets up monitoring.

Usage:
    python src/helper/setup_linkedin_research.py

⚠️ SAFETY NOTICE:
- Only use with a dedicated LinkedIn account (not your main account)
- All research follows LinkedIn's Terms of Service
- No automated high-volume requests during research phase
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class LinkedInResearchSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.research_dir = self.project_root / "research" / "linkedin"
        self.research_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_browser_profiles(self):
        """Create isolated browser profiles for LinkedIn research"""
        print("🔧 Setting up browser profiles...")
        
        # Chrome research profile
        chrome_profile = self.research_dir / "chrome_profile"
        chrome_profile.mkdir(exist_ok=True)
        
        # Firefox research profile  
        firefox_profile = self.research_dir / "firefox_profile"
        firefox_profile.mkdir(exist_ok=True)
        
        print(f"✅ Browser profiles created:")
        print(f"   Chrome: {chrome_profile}")
        print(f"   Firefox: {firefox_profile}")
        
        return {
            'chrome': chrome_profile,
            'firefox': firefox_profile
        }
    
    def install_research_dependencies(self):
        """Install additional packages needed for LinkedIn research"""
        print("📦 Installing research dependencies...")
        
        research_packages = [
            'playwright',           # Browser automation
            'mitmproxy',           # Network traffic analysis  
            'requests-html',       # Advanced requests
            'selenium-wire',       # Enhanced Selenium with request capture
            'fake-useragent',      # User agent rotation
        ]
        
        for package in research_packages:
            try:
                print(f"   Installing {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], check=True, capture_output=True)
                print(f"   ✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Failed to install {package}: {e}")
        
        # Install Playwright browsers
        try:
            print("   Installing Playwright browsers...")
            subprocess.run([
                sys.executable, '-m', 'playwright', 'install'
            ], check=True, capture_output=True)
            print("   ✅ Playwright browsers installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Failed to install Playwright browsers: {e}")
    
    def create_research_config(self):
        """Create configuration file for research settings"""
        print("⚙️ Creating research configuration...")
        
        config = {
            "research_settings": {
                "max_requests_per_hour": 10,
                "delay_between_requests": 5,
                "max_daily_requests": 50,
                "use_random_delays": True,
                "respect_rate_limits": True
            },
            "browser_settings": {
                "headless": False,
                "slow_mo": 100,
                "user_agent_rotation": True,
                "clear_cookies_between_sessions": True
            },
            "monitoring": {
                "log_all_requests": True,
                "capture_responses": True,
                "alert_on_rate_limit": True,
                "save_har_files": True
            },
            "safety_measures": {
                "use_vpn": True,
                "separate_account_only": True,
                "no_production_data": True,
                "respect_tos": True
            }
        }
        
        config_file = self.research_dir / "research_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to: {config_file}")
        return config_file
    
    def create_research_scripts(self):
        """Create helper scripts for LinkedIn research"""
        print("📝 Creating research scripts...")
        
        # Browser launcher script
        launcher_script = self.research_dir / "launch_research_browser.py"
        launcher_content = '''"""
LinkedIn Research Browser Launcher

Safe browser configuration for LinkedIn research with monitoring enabled.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def launch_research_browser():
    """Launch browser with research-safe configuration"""
    
    async with async_playwright() as p:
        # Launch with research profile
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,  # Human-like timing
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        )
        
        # Create context with monitoring
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            accept_downloads=True
        )
        
        # Enable request monitoring
        def log_request(request):
            print(f"Request: {request.method} {request.url}")
            
        def log_response(response):
            if 'linkedin.com' in response.url:
                print(f"Response: {response.status} {response.url}")
        
        context.on('request', log_request)
        context.on('response', log_response)
        
        # Open LinkedIn
        page = await context.new_page()
        await page.goto('https://linkedin.com/jobs')
        
        print("Research browser ready!")
        print("Use this browser for manual LinkedIn research")
        print("Dev tools are available for network analysis")
        print("Remember: Keep requests human-paced!")
        
        # Keep browser open for research
        await page.wait_for_timeout(300000)  # 5 minutes
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(launch_research_browser())
'''
        
        with open(launcher_script, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # Request monitor script
        monitor_script = self.research_dir / "monitor_requests.py"
        monitor_content = '''"""
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
'''
        
        with open(monitor_script, 'w', encoding='utf-8') as f:
            f.write(monitor_content)
        
        print(f"✅ Research scripts created:")
        print(f"   Browser launcher: {launcher_script}")
        print(f"   Request monitor: {monitor_script}")
    
    def create_safety_checklist(self):
        """Create safety checklist for researchers"""
        print("📋 Creating safety checklist...")
        
        checklist_content = """# LinkedIn Research Safety Checklist

**Before Starting Research:**

## Account Safety
- [ ] Using separate LinkedIn account (not main account)
- [ ] VPN enabled for IP protection
- [ ] Browser in incognito/private mode
- [ ] Research profile configured correctly

## Technical Setup
- [ ] Browser dev tools ready
- [ ] Request monitoring enabled
- [ ] Rate limiting configured (max 10 requests/hour)
- [ ] Session logging activated

## Legal Compliance  
- [ ] Read and understand LinkedIn Terms of Service
- [ ] Research limited to public job posting data
- [ ] No personal data collection from other users
- [ ] Respectful scraping practices enabled

## Research Protocol
- [ ] Manual browsing pace (human-like timing)
- [ ] Document findings in research notes
- [ ] Save network requests for analysis
- [ ] Monitor for any account warnings

**During Research:**

## Rate Limiting Compliance
- [ ] Maximum 10 job searches per hour
- [ ] 5+ second delays between requests
- [ ] Stop immediately if rate limit detected
- [ ] Monitor response times for throttling

## Data Collection Guidelines
- [ ] Focus only on job posting information
- [ ] No collection of user profiles or personal data
- [ ] Anonymize any data saved in documentation
- [ ] Use placeholder company names in examples

## Behavioral Guidelines
- [ ] Vary search patterns (don't repeat same query)
- [ ] Mix manual browsing with research activities  
- [ ] Take breaks between research sessions
- [ ] Clear cookies between major research phases

**After Research:**

## Data Handling
- [ ] Anonymize all collected data
- [ ] Remove any authentication tokens from logs
- [ ] Update research notes with findings
- [ ] Commit anonymized findings to git

## Safety Verification
- [ ] Check LinkedIn account for any restrictions
- [ ] Verify no ToS violation warnings received
- [ ] Confirm no unusual account activity
- [ ] Document any issues encountered

## Documentation
- [ ] Update linkedin_research_notes.md
- [ ] Save session logs with timestamps
- [ ] Document any new API endpoints discovered
- [ ] Note rate limiting behavior observed

---

**🚨 EMERGENCY PROCEDURES**

**If Account Restricted:**
1. Stop all research immediately
2. Document the restriction details
3. Wait 24-48 hours before assessing
4. Update research notes with lessons learned

**If Rate Limited:**
1. Stop current session immediately
2. Document the trigger conditions
3. Wait for rate limit reset (usually 1 hour)
4. Adjust research pace for future sessions

**If ToS Warning Received:**
1. Cease all research activities
2. Review and document the warning
3. Reassess research methodology
4. Consider alternative approaches

---

**Remember**: This is RESEARCH ONLY. No production automation until safety confirmed!
"""
        
        checklist_file = self.research_dir / "SAFETY_CHECKLIST.md"
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        print(f"✅ Safety checklist created: {checklist_file}")
    
    def setup_monitoring_directory(self):
        """Create directory structure for monitoring data"""
        print("📁 Setting up monitoring directories...")
        
        directories = [
            self.research_dir / "session_logs",
            self.research_dir / "har_files", 
            self.research_dir / "screenshots",
            self.research_dir / "api_samples"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
        # Create README for each directory
        readmes = {
            "session_logs": "Session logs from research activities",
            "har_files": "HTTP Archive files from browser sessions", 
            "screenshots": "Screenshots of interesting findings",
            "api_samples": "Sample API responses (anonymized)"
        }
        
        for directory in directories:
            readme_file = directory / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(f"# {directory.name}\n\n{readmes[directory.name]}\n")
        
        print(f"✅ Monitoring directories created:")
        for directory in directories:
            print(f"   {directory}")
    
    def run_setup(self):
        """Run complete LinkedIn research environment setup"""
        print("🚀 Setting up LinkedIn Research Environment...")
        print("=" * 60)
        
        try:
            # Setup components
            profiles = self.setup_browser_profiles()
            self.install_research_dependencies()
            config_file = self.create_research_config()
            self.create_research_scripts()
            self.create_safety_checklist()
            self.setup_monitoring_directory()
            
            print("\n" + "=" * 60)
            print("✅ LinkedIn Research Environment Setup Complete!")
            print("\n🎯 Next Steps:")
            print("1. Read the safety checklist carefully")
            print("2. Set up separate LinkedIn account for research")
            print("3. Enable VPN for IP protection")
            print("4. Run: python research/linkedin/launch_research_browser.py")
            print("5. Begin manual analysis with dev tools")
            
            print(f"\n📁 Research directory: {self.research_dir}")
            print(f"📋 Safety checklist: {self.research_dir}/SAFETY_CHECKLIST.md")
            print(f"⚙️ Configuration: {config_file}")
            
            print("\n⚠️ REMEMBER:")
            print("- Use separate LinkedIn account only")
            print("- Follow rate limiting guidelines")
            print("- Respect LinkedIn's Terms of Service")
            print("- Document everything for learning")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False
        
        return True

def main():
    """Main setup function"""
    setup = LinkedInResearchSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup successful! Ready for LinkedIn research.")
    else:
        print("\n💥 Setup failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()