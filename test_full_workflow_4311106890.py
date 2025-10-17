#!/usr/bin/env python3
"""Test full workflow: LinkedIn scrape → Trello card creation."""

import sys
sys.path.insert(0, 'src')

from linkedin_scraper import scrape_linkedin_job
from trello_connect import TrelloConnect
import json
import time

url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890"

print(f"Testing full workflow for URL: {url}\n")
print("=" * 80)

# Step 1: Scrape
print("\n📍 STEP 1: Scraping LinkedIn job...")
try:
    job_data = scrape_linkedin_job(url)
    print(f"✅ Scraped successfully")
    print(f"\nJob Data:")
    print(json.dumps(job_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Scraping failed: {e}")
    sys.exit(1)

# Step 2: Create Trello card
print("\n" + "=" * 80)
print("\n📍 STEP 2: Creating Trello card...")
try:
    trello = TrelloConnect()
    print(f"✅ TrelloConnect initialized")
    print(f"   Board ID: {trello.board_id}")
    print(f"   List ID: {trello.leads_list_id}")
    
    card_id = trello.create_card_from_job_data(job_data)
    print(f"✅ Card created with ID: {card_id}")
    
    # Wait a moment for Trello to process
    time.sleep(2)
    
except Exception as e:
    print(f"❌ Trello card creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Inspect created card
print("\n" + "=" * 80)
print("\n📍 STEP 3: Inspecting created card...")
try:
    import requests
    from src.utils.config import get_str
    
    trello_key = get_str('TRELLO_KEY')
    trello_token = get_str('TRELLO_TOKEN')
    
    url_get = f"https://api.trello.com/1/cards/{card_id}?key={trello_key}&token={trello_token}"
    
    # Get basic card info
    response = requests.get(url_get, timeout=5)
    card_info = response.json()
    
    print(f"✅ Card fetched from Trello API")
    print(f"\nBasic Info:")
    print(f"  Name: {card_info.get('name', 'N/A')}")
    print(f"  URL: {card_info.get('url', 'N/A')}")
    print(f"  Description length: {len(card_info.get('desc', ''))} chars")
    
    # Get custom fields
    url_fields = f"https://api.trello.com/1/cards/{card_id}/customFieldItems?key={trello_key}&token={trello_token}"
    response = requests.get(url_fields, timeout=5)
    fields = response.json()
    
    print(f"\n📋 Custom Fields:")
    for field in fields:
        field_id = field.get('idCustomField')
        value = field.get('value', {})
        if 'text' in value:
            print(f"  Field {field_id}: {value.get('text', 'N/A')}")
        elif 'idValue' in value:
            print(f"  Field {field_id}: {value.get('idValue', 'N/A')}")
    
    # Get attachments
    url_attach = f"https://api.trello.com/1/cards/{card_id}/attachments?key={trello_key}&token={trello_token}"
    response = requests.get(url_attach, timeout=5)
    attachments = response.json()
    
    print(f"\n🔗 Attachments ({len(attachments)} total):")
    for attach in attachments:
        print(f"  - {attach.get('name', 'N/A')}: {attach.get('url', 'N/A')}")
    
    # Get labels
    print(f"\n🏷️  Labels ({len(card_info.get('labels', []))} total):")
    for label in card_info.get('labels', []):
        print(f"  - {label.get('name', 'N/A')}")
    
except Exception as e:
    print(f"❌ Card inspection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("\n✅ Test complete!")
print(f"\nManually inspect card at: https://trello.com/c/{card_id}")
