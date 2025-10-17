"""Quick check of Trello card location"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env
from utils.trello import TRELLO_API_BASE, get_auth_params

load_env()
auth = get_auth_params()
card_id = '68ee39617a77f92dcc6b1e9b'

resp = requests.get(f'{TRELLO_API_BASE}/cards/{card_id}', params=auth, timeout=30)
card = resp.json()

print('=' * 70)
print('TRELLO CARD LOCATION CHECK')
print('=' * 70)
print(f'Card: {card.get("name", "N/A")}')
print(f'URL: {card.get("shortUrl", "N/A")}')
print()
print('Location fields:')
print(f'  address: {card.get("address", "N/A")}')
print(f'  locationName: {card.get("locationName", "N/A")}')
print(f'  coordinates: {card.get("coordinates", "N/A")}')
print('=' * 70)
