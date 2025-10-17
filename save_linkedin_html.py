#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Save LinkedIn page HTML to file for inspection."""

import requests
from pathlib import Path

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"

print(f"Fetching: {url}")
response = requests.get(url, timeout=10)

output_file = Path("linkedin_page.html")
output_file.write_text(response.text, encoding='utf-8')

print(f"Saved to: {output_file}")
print(f"File size: {len(response.text)} chars")

# Quick analysis
print("\nQuick checks:")
print(f"  'Show more' in page: {'Show more' in response.text}")
print(f"  'show-more' in page: {'show-more' in response.text}")
print(f"  'See more' in page: {'See more' in response.text}")
print(f"  'data-test-id' count: {response.text.count('data-test-id')}")

# Find job description patterns
lines = response.text.split('\n')
desc_lines = [l for l in lines if 'description' in l.lower() or 'job-details' in l.lower()]
print(f"\nLines with 'description' or 'job-details': {len(desc_lines)}")
for line in desc_lines[:5]:
    print(f"  {line[:150]}")
