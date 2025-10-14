"""
Compare location data between Toll Collect (working) and WERTGARANTIE (not working)
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env
from utils.trello import TRELLO_API_BASE, get_auth_params

load_env()
auth = get_auth_params()

cards = {
    'Toll Collect (Berlin - HAS MAP)': '68ee39617a77f92dcc6b1e9b',
    'WERTGARANTIE (Hannover - NO MAP)': '68ee3abe7cc543a94737df78'
}

print('=' * 80)
print('COMPARING LOCATION DATA BETWEEN CARDS')
print('=' * 80)

for name, card_id in cards.items():
    print(f'\n{name}:')
    print('-' * 80)
    
    resp = requests.get(f'{TRELLO_API_BASE}/cards/{card_id}', params=auth, timeout=30)
    if resp.status_code == 200:
        card = resp.json()
        
        # Check all possible location-related fields
        location_fields = {
            'address': card.get('address'),
            'locationName': card.get('locationName'),
            'coordinates': card.get('coordinates'),
            'location': card.get('location'),
            'loc': card.get('loc'),
            'name': card.get('name'),
        }
        
        print(f"Card name: {card.get('name')}")
        print(f"\nLocation fields:")
        for field, value in location_fields.items():
            if value is not None and value != '':
                print(f"  {field}: {value}")
        
        # Check if there are any fields we haven't printed
        print(f"\nAll card keys (first 20):")
        keys = list(card.keys())[:20]
        print(f"  {', '.join(keys)}")
    else:
        print(f"Failed to fetch card: {resp.status_code}")

print('\n' + '=' * 80)
