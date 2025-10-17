"""
Script to inspect Trello custom field values (Quelle dropdown options)
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
FIELD_QUELLE = get_str('TRELLO_FIELD_QUELLE')

# Get all cards to find examples
url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
params = {
    'key': API_KEY,
    'token': TOKEN,
    'customFieldItems': 'true'
}

response = requests.get(url, params=params)
cards = response.json()

print(f"Found {len(cards)} cards on board")
print("=" * 80)

for card in cards[:5]:  # Show first 5 cards
    print(f"\nCard: {card['name']}")
    print(f"ID: {card['id']}")
    
    # Get card details including custom fields
    card_url = f"https://api.trello.com/1/cards/{card['id']}"
    card_resp = requests.get(card_url, params={'key': API_KEY, 'token': TOKEN})
    card_detail = card_resp.json()
    
    if 'customFieldItems' in card_detail:
        print("Custom Fields:")
        for cf in card_detail['customFieldItems']:
            print(f"  Field ID: {cf.get('idCustomField')}")
            if cf.get('idValue'):
                print(f"  Value (ID): {cf.get('idValue')}")
                print(f"  Value (Text): {cf.get('value')}")
            else:
                print(f"  Value: {cf.get('value', 'N/A')}")

# Get field definition to see all options
print("\n" + "=" * 80)
print(f"Quelle Field ID: {FIELD_QUELLE}")
print("=" * 80)

field_url = f"https://api.trello.com/1/customFields/{FIELD_QUELLE}"
field_resp = requests.get(field_url, params={'key': API_KEY, 'token': TOKEN})
field_detail = field_resp.json()

print(f"\nField Name: {field_detail.get('name')}")
print(f"Field Type: {field_detail.get('type')}")
print(f"Field Display: {field_detail.get('display', {}).get('cardFront')}")

if field_detail.get('options'):
    print("\nAvailable Options:")
    for i, opt in enumerate(field_detail['options']):
        print(f"  {i+1}. {opt.get('value', 'Unknown')}")
        print(f"     ID: {opt.get('id')}")
        print()
