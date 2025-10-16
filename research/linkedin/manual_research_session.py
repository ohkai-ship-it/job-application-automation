"""
LinkedIn Browser Research - Manual Analysis Helper

This script opens a research-configured browser for manual LinkedIn analysis.
It provides dev tools monitoring and logging while keeping everything manual and safe.

Usage:
    python research/linkedin/manual_research_session.py

Safety: This is 100% manual browsing with monitoring - no automation.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

"""
LinkedIn Browser Research - Manual Analysis Helper

This script opens a research-configured browser for manual LinkedIn analysis.
It provides dev tools monitoring and logging while keeping everything manual and safe.

Usage:
    python research/linkedin/manual_research_session.py

Safety: This is 100% manual browsing with monitoring - no automation.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import sys

def create_research_session():
    """Create a new research session with logging"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_name = f"linkedin_research_{timestamp}"
    
    research_dir = Path("research/linkedin")
    session_log_dir = research_dir / "session_logs"
    session_log_dir.mkdir(exist_ok=True)
    
    session_file = session_log_dir / f"{session_name}.json"
    
    session_data = {
        "session_name": session_name,
        "start_time": timestamp,
        "research_goals": [
            "Analyze LinkedIn job search network requests",
            "Identify API endpoints used for job listings",
            "Document authentication requirements",
            "Test rate limiting behavior",
            "Capture response data structures"
        ],
        "safety_checklist": {
            "separate_account": False,
            "vpn_enabled": False,
            "dev_tools_ready": False,
            "rate_limiting_configured": False
        },
        "findings": [],
        "requests_captured": [],
        "notes": []
    }
    
    return session_file, session_data

def safety_check():
    """Perform safety checklist before starting research"""
    print("🛡️ LinkedIn Research Safety Check")
    print("=" * 50)
    
    checks = [
        ("Using separate LinkedIn account (not main account)", "separate_account"),
        ("VPN enabled for IP protection", "vpn_enabled"), 
        ("Browser dev tools ready", "dev_tools_ready"),
        ("Rate limiting understood (max 10 requests/hour)", "rate_limiting_configured")
    ]
    
    results = {}
    
    for check_text, check_key in checks:
        while True:
            response = input(f"✓ {check_text}? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                results[check_key] = True
                print(f"  ✅ Confirmed: {check_text}")
                break
            elif response in ['n', 'no']:
                results[check_key] = False
                print(f"  ❌ NOT READY: {check_text}")
                print(f"  Please complete this requirement before continuing.")
                return False, results
            else:
                print("  Please answer 'y' or 'n'")
    
    print("\n✅ All safety checks passed! Ready to begin research.")
    return True, results

def open_research_browser():
    """Open Chrome with research configuration"""
    print("\n🔧 Opening research browser...")
    
    # Chrome with dev tools and research profile
    chrome_args = [
        "--user-data-dir=research/linkedin/chrome_profile",
        "--disable-blink-features=AutomationControlled",
        "--disable-automation", 
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--remote-debugging-port=9222"
    ]
    
    try:
        # Try to open Chrome
        if sys.platform.startswith('win'):
            subprocess.Popen(['chrome'] + chrome_args)
        else:
            subprocess.Popen(['google-chrome'] + chrome_args)
        
        print("✅ Chrome opened with research configuration")
        print("🔧 Dev tools will be available on localhost:9222")
        
    except Exception as e:
        print(f"⚠️ Could not open Chrome automatically: {e}")
        print("Please open Chrome manually with these arguments:")
        print(" ".join(chrome_args))

def research_instructions():
    """Display research instructions"""
    print("\n📋 LinkedIn Research Instructions")
    print("=" * 50)
    
    instructions = [
        "1. Navigate to https://linkedin.com/jobs",
        "2. Open Chrome Dev Tools (F12)",
        "3. Go to Network tab, clear any existing requests",
        "4. Perform manual job search: 'Python Developer Hamburg'",
        "5. Observe network requests in dev tools",
        "6. Look for API endpoints (especially /voyager/api/ patterns)",
        "7. Click on individual job postings to see detail requests",
        "8. Right-click network requests → Copy → Copy as HAR",
        "9. Save HAR files to research/linkedin/har_files/",
        "10. Document findings in session notes"
    ]
    
    for instruction in instructions:
        print(f"  {instruction}")
    
    print("\n🎯 What to Look For:")
    print("  - API endpoint URLs (especially /voyager/api/)")
    print("  - Request headers (authentication, CSRF tokens)")  
    print("  - Response data structures (job data format)")
    print("  - Rate limiting headers (X-RateLimit-*, Retry-After)")
    print("  - Authentication requirements")
    
    print("\n⚠️ Important Reminders:")
    print("  - Keep manual pace (5+ seconds between actions)")
    print("  - Don't repeat same search multiple times")
    print("  - Stop if you see any rate limiting warnings")
    print("  - Save interesting requests as HAR files")

def session_logging():
    """Interactive session logging"""
    print("\n📝 Session Logging")
    print("=" * 30)
    
    findings = []
    
    while True:
        print("\nWhat would you like to log?")
        print("1. API endpoint discovered")
        print("2. Authentication observation") 
        print("3. Rate limiting behavior")
        print("4. Data structure finding")
        print("5. General note")
        print("6. Finish session")
        
        choice = input("\nChoice (1-6): ").strip()
        
        if choice == "1":
            endpoint = input("API endpoint URL: ")
            method = input("HTTP method (GET/POST): ")
            purpose = input("What does this endpoint do?: ")
            findings.append({
                "type": "api_endpoint",
                "endpoint": endpoint,
                "method": method,
                "purpose": purpose,
                "timestamp": datetime.now().isoformat()
            })
            print("✅ API endpoint logged")
            
        elif choice == "2":
            auth_type = input("Authentication method observed: ")
            details = input("Details (headers, tokens, etc.): ")
            findings.append({
                "type": "authentication",
                "method": auth_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
            print("✅ Authentication finding logged")
            
        elif choice == "3":
            behavior = input("Rate limiting behavior observed: ")
            triggers = input("What triggered it?: ")
            findings.append({
                "type": "rate_limiting",
                "behavior": behavior,
                "triggers": triggers,
                "timestamp": datetime.now().isoformat()
            })
            print("✅ Rate limiting observation logged")
            
        elif choice == "4":
            data_type = input("Data structure (job listing, company, etc.): ")
            format_info = input("Structure details: ")
            findings.append({
                "type": "data_structure",
                "data_type": data_type,
                "format": format_info,
                "timestamp": datetime.now().isoformat()
            })
            print("✅ Data structure logged")
            
        elif choice == "5":
            note = input("General note: ")
            findings.append({
                "type": "general_note",
                "note": note,
                "timestamp": datetime.now().isoformat()
            })
            print("✅ Note logged")
            
        elif choice == "6":
            break
            
        else:
            print("Invalid choice, please select 1-6")
    
    return findings

def save_session(session_file, session_data, safety_results, findings):
    """Save the research session data"""
    session_data["safety_checklist"] = safety_results
    session_data["findings"] = findings
    session_data["end_time"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_data["duration_minutes"] = "TBD"  # Could calculate if needed
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)
    
    print(f"\n💾 Session saved: {session_file}")
    print(f"📊 Logged {len(findings)} findings")
    
    # Update research notes
    update_research_notes(findings)

def update_research_notes(findings):
    """Update the main research notes file"""
    notes_file = Path("docs/linkedin_research_notes.md")
    
    if findings:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        update_text = f"\n\n### Research Session Update - {timestamp}\n\n"
        
        for finding in findings:
            if finding["type"] == "api_endpoint":
                update_text += f"**API Endpoint Found**: {finding['endpoint']} ({finding['method']})\n"
                update_text += f"- Purpose: {finding['purpose']}\n\n"
            elif finding["type"] == "authentication":
                update_text += f"**Authentication**: {finding['method']}\n"
                update_text += f"- Details: {finding['details']}\n\n"
            elif finding["type"] == "rate_limiting":
                update_text += f"**Rate Limiting**: {finding['behavior']}\n"
                update_text += f"- Triggered by: {finding['triggers']}\n\n"
            elif finding["type"] == "data_structure":
                update_text += f"**Data Structure** ({finding['data_type']}): {finding['format']}\n\n"
            elif finding["type"] == "general_note":
                update_text += f"**Note**: {finding['note']}\n\n"
        
        # Append to research notes
        with open(notes_file, 'a', encoding='utf-8') as f:
            f.write(update_text)
        
        print(f"📝 Research notes updated: {notes_file}")

def main():
    """Main research session workflow"""
    print("🔍 LinkedIn Manual Research Session")
    print("=" * 50)
    print("This tool helps you safely analyze LinkedIn's job search functionality.")
    print("All research is manual - this tool only provides guidance and logging.\n")
    
    # Create session
    session_file, session_data = create_research_session()
    print(f"📁 Session: {session_data['session_name']}")
    
    # Safety check
    safety_passed, safety_results = safety_check()
    if not safety_passed:
        print("\n❌ Safety checks failed. Please complete requirements before continuing.")
        return
    
    # Open browser
    open_research_browser()
    
    # Show instructions
    research_instructions()
    
    # Wait for user to begin research
    input("\n⏰ Press Enter when you're ready to begin research...")
    
    print("\n🔍 Research in progress...")
    print("Take your time and follow the instructions above.")
    print("Remember: Manual pace, document everything, respect rate limits!")
    
    # When done, log findings
    input("\n✅ Press Enter when you've completed the research...")
    
    # Interactive logging
    findings = session_logging()
    
    # Save session
    save_session(session_file, session_data, safety_results, findings)
    
    print("\n🎉 Research session complete!")
    print("Next steps:")
    print("1. Review HAR files saved in research/linkedin/har_files/")
    print("2. Analyze API endpoints discovered") 
    print("3. Plan next research phase (mobile APIs)")
    print("4. Update technical architecture design")

if __name__ == "__main__":
    main()
