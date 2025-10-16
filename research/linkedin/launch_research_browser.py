"""
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
