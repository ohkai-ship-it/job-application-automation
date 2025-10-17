#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Investigate LinkedIn page structure to find full job description."""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, 'src')

import requests
from bs4 import BeautifulSoup
import json

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"

print("Fetching LinkedIn page...\n")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("=" * 80)
    print("INVESTIGATION: Full Job Description Extraction")
    print("=" * 80)
    
    # Strategy 1: Look for script tags with JSON data (LinkedIn embeds data in window objects)
    print("\n[STRATEGY 1] Check for embedded JSON in <script> tags")
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    print(f"  Found {len(script_tags)} ld+json script tags")
    
    for i, script in enumerate(script_tags[:3]):  # Check first 3
        try:
            data = json.loads(script.string)
            if 'description' in data:
                desc = data['description']
                print(f"\n  Script {i}: Found description, length: {len(desc)} chars")
                print(f"  Preview: {desc[:200]}...")
        except:
            pass
    
    # Strategy 2: Look for description in common divs
    print("\n[STRATEGY 2] Check common description divs")
    description_divs = [
        soup.find('div', {'class': lambda x: x and 'description' in x.lower() if x else False}),
        soup.find('div', {'data-test-id': lambda x: x and 'description' in x.lower() if x else False}),
        soup.find('section', {'data-test-id': lambda x: x and 'description' in x.lower() if x else False}),
        soup.find('div', {'id': lambda x: x and 'description' in x.lower() if x else False}),
    ]
    
    for i, div in enumerate(description_divs):
        if div:
            text = div.get_text(strip=True)
            if text and len(text) > 100:
                print(f"  Found in div {i}: {len(text)} chars")
                print(f"  Preview: {text[:200]}...")
    
    # Strategy 3: Look for show-more/expand buttons that might indicate truncation
    print("\n[STRATEGY 3] Check for truncation indicators")
    show_more = soup.find('button', {'aria-label': lambda x: x and 'show more' in x.lower() if x else False})
    if show_more:
        print(f"  ✓ Found 'Show More' button - description is TRUNCATED (needs JS execution)")
    
    see_more = soup.find_all(string=lambda text: text and 'see more' in text.lower() if text else False)
    if see_more:
        print(f"  ✓ Found 'See more' text - description is TRUNCATED (needs JS execution)")
    
    # Strategy 4: Check for hidden/collapsed sections
    print("\n[STRATEGY 4] Check for hidden content")
    hidden_divs = soup.find_all('div', {'style': lambda x: x and 'display:none' in x if x else False})
    print(f"  Found {len(hidden_divs)} hidden divs")
    
    collapsed_sections = soup.find_all('div', {'data-test-id': lambda x: x and 'job-details' in x.lower() if x else False})
    print(f"  Found {len(collapsed_sections)} job-details sections")
    if collapsed_sections:
        for sec in collapsed_sections[:2]:
            text = sec.get_text(strip=True)
            if len(text) > 100:
                print(f"    Section length: {len(text)} chars")
                print(f"    Preview: {text[:200]}...")
    
    # Strategy 5: Look at all paragraphs and list items
    print("\n[STRATEGY 5] Aggregate all text content")
    all_text = []
    for p in soup.find_all(['p', 'li', 'div']):
        text = p.get_text(strip=True)
        if 100 < len(text) < 5000:  # Reasonable length
            all_text.append(text)
    
    if all_text:
        full_text = ' '.join(all_text)
        print(f"  Aggregated text length: {len(full_text)} chars")
        if len(full_text) > 500:
            print(f"  ✓ Successfully aggregated substantial content")
            print(f"  Preview: {full_text[:300]}...")
    
    # Strategy 6: Look for specific LinkedIn job description structure
    print("\n[STRATEGY 6] LinkedIn-specific selectors")
    selectors_to_try = [
        'div[data-test-id="job-details-jobs-details__main-content"]',
        'div[class*="show-more-less"]',
        'div[class*="description"]',
        'article',
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        if elements:
            print(f"  Selector '{selector}': Found {len(elements)} elements")
            for elem in elements[:1]:
                text = elem.get_text(strip=True)
                if len(text) > 100:
                    print(f"    Length: {len(text)} chars")
    
    print("\n" + "=" * 80)
    print("\nSUMMARY:")
    print("  1. Check if full description is in JSON-LD or other script tags")
    print("  2. LinkedIn likely requires JS execution for full text (truncated with 'Show more')")
    print("  3. Solution options:")
    print("     a) Use Playwright/Selenium to execute JS and expand description")
    print("     b) Parse page source more aggressively (aggregate all paragraphs)")
    print("     c) Use LinkedIn's API if available (requires auth)")
    print("     d) Accept truncated text and use cover letter with what's available")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
