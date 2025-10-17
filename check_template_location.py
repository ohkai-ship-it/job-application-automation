"""Check template card for location settings"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

load_env()
auth = get_auth_params()
template_id = get_str('TRELLO_TEMPLATE_CARD_ID')

print('=' * 70)
print('TEMPLATE CARD LOCATION CHECK')
print('=' * 70)

resp = requests.get(f'{TRELLO_API_BASE}/cards/{template_id}', params=auth, timeout=30)
if resp.status_code == 200:
    card = resp.json()
    print(f'Template Card: {card.get("name", "N/A")}')
    print(f'URL: {card.get("shortUrl", "N/A")}')
    print()
    print('Location fields:')
    print(f'  address: {card.get("address", "N/A")}')
    print(f'  locationName: {card.get("locationName", "N/A")}')
    print(f'  coordinates: {card.get("coordinates", "N/A")}')
else:
    print(f'Failed to get template card: {resp.status_code}')

print('=' * 70)
