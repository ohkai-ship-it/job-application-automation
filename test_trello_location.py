"""
Test script to check Trello location/coordinates API
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def test_location_api():
    load_env()
    auth = get_auth_params()
    
    # Get the Toll Collect card
    card_id = "68ee39617a77f92dcc6b1e9b"  # From the logs
    
    print("Testing different location API approaches:\n")
    print("=" * 70)
    
    # Method 1: Check current card fields
    print("\n1. Current card data:")
    card_url = f"{TRELLO_API_BASE}/cards/{card_id}"
    resp = requests.get(card_url, params=auth, timeout=30)
    if resp.status_code == 200:
        card = resp.json()
        print(f"  address: {card.get('address', 'N/A')}")
        print(f"  coordinates: {card.get('coordinates', 'N/A')}")
        print(f"  locationName: {card.get('locationName', 'N/A')}")
    
    # Method 2: Try updating with address field
    print("\n2. Trying PUT with 'address' field:")
    payload = {'address': 'Berlin, Germany'}
    resp = requests.put(card_url, params=auth, json=payload, timeout=30)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        card = resp.json()
        print(f"  address: {card.get('address', 'N/A')}")
        print(f"  coordinates: {card.get('coordinates', 'N/A')}")
    
    # Method 3: Try updating with coordinates + name
    print("\n3. Trying PUT with 'coordinates' field:")
    # Berlin coordinates: 52.52, 13.405
    payload = {
        'coordinates': '52.52,13.405'
    }
    resp = requests.put(card_url, params=auth, json=payload, timeout=30)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        card = resp.json()
        print(f"  address: {card.get('address', 'N/A')}")
        print(f"  coordinates: {card.get('coordinates', 'N/A')}")
    
    # Method 4: Try locationName
    print("\n4. Trying PUT with 'locationName' field:")
    payload = {'locationName': 'Berlin, Germany'}
    resp = requests.put(card_url, params=auth, json=payload, timeout=30)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        card = resp.json()
        print(f"  address: {card.get('address', 'N/A')}")
        print(f"  locationName: {card.get('locationName', 'N/A')}")
        print(f"  coordinates: {card.get('coordinates', 'N/A')}")
    
    # Final check
    print("\n" + "=" * 70)
    print("FINAL CARD STATE:")
    resp = requests.get(card_url, params=auth, timeout=30)
    if resp.status_code == 200:
        card = resp.json()
        print(f"  address: {card.get('address', 'N/A')}")
        print(f"  locationName: {card.get('locationName', 'N/A')}")
        print(f"  coordinates: {card.get('coordinates', 'N/A')}")
    print("=" * 70)

if __name__ == "__main__":
    test_location_api()
