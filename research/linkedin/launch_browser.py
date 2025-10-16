"""
Simple LinkedIn Research Browser Launcher

This script provides the Chrome command to launch the research browser.
Copy and paste the command into your terminal to start the research browser.
"""

import sys
from pathlib import Path

def main():
    """Display browser launch instructions"""
    
    print("🔍 LinkedIn Research Browser Launcher")
    print("=" * 50)
    
    # Get the research profile path
    research_dir = Path("research/linkedin/chrome_profile").resolve()
    
    print(f"\n📁 Research Profile: {research_dir}")
    print("\n🔧 Chrome Launch Command:")
    print("Copy and paste this command into a new terminal:")
    print()
    
    # Chrome command for Windows
    if sys.platform.startswith('win'):
        cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --user-data-dir="{research_dir}" --disable-blink-features=AutomationControlled --disable-automation --no-sandbox --disable-dev-shm-usage'
        print(f"  {cmd}")
    else:
        cmd = f'google-chrome --user-data-dir="{research_dir}" --disable-blink-features=AutomationControlled --disable-automation --no-sandbox --disable-dev-shm-usage'
        print(f"  {cmd}")
    
    print("\n📋 After Chrome Opens:")
    print("1. Navigate to: https://linkedin.com/jobs")
    print("2. Log in with your research account")
    print("3. Open Dev Tools (F12)")
    print("4. Go to Network tab")
    print("5. Clear existing requests")
    print("6. Start your research!")
    
    print("\n🎯 Research Goals:")
    print("- Search: 'Python Developer Hamburg'")
    print("- Look for /voyager/api/ endpoints")
    print("- Document request headers")
    print("- Save interesting responses")
    print("- Note rate limiting behavior")
    
    print("\n⚠️ Safety Reminders:")
    print("- Keep human-like pace (5+ seconds between actions)")
    print("- Max 10 searches per hour")
    print("- Stop if you see rate limit warnings")
    print("- Document everything you discover")

if __name__ == "__main__":
    main()