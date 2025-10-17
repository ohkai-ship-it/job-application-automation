"""
Find portal/website/link fields in Trello
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
from src.utils.env import load_env, get_str

load_env()

API_KEY = get_str('TRELLO_KEY')
TOKEN = get_str('TRELLO_TOKEN')
BOARD_ID = get_str('TRELLO_BOARD_ID')

# Get all custom fields
url = f"https://api.trello.com/1/boards/{BOARD_ID}/customFields"
params = {'key': API_KEY, 'token': TOKEN}

response = requests.get(url, params=params)
fields = response.json()

print("All Custom Fields:")
print("=" * 80)

for field in fields:
    name = field['name']
    field_id = field['id']
    field_type = field.get('type', 'unknown')
    
    print(f"\n{name}")
    print(f"  ID: {field_id}")
    print(f"  Type: {field_type}")
    
    # Highlight fields that might be for URLs/websites/portals
    if any(keyword in name.lower() for keyword in ['portal', 'website', 'link', 'url', 'company', 'homepage']):
        print("  --> RELEVANT FOR COMPANY PORTAL")
