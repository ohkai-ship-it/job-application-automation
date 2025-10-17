"""Check if Hannover now has coordinates"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env
from utils.trello import TRELLO_API_BASE, get_auth_params

load_env()
auth = get_auth_params()

card = requests.get(f'{TRELLO_API_BASE}/cards/68ee3abe7cc543a94737df78?fields=all', params=auth).json()

print('=' * 70)
print('WERTGARANTIE CARD - LOCATION CHECK AFTER UPDATE')
print('=' * 70)
print(f"Card: {card.get('name')}")
print(f"\nLocation data:")
print(f"  address: {card.get('address')}")
print(f"  locationName: {card.get('locationName')}")
print(f"  coordinates: {card.get('coordinates')}")
print(f"  has map: {'Yes ✓' if card.get('staticMapUrl') else 'No ✗'}")
print('=' * 70)
