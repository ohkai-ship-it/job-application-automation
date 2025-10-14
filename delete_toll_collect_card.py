"""
Quick script to delete a specific Trello card by ID
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def delete_card(card_id: str):
    load_env()
    auth = get_auth_params()
    
    # Get card info first
    card_url = f"{TRELLO_API_BASE}/cards/{card_id}"
    resp = requests.get(card_url, params=auth, timeout=30)
    
    if resp.status_code == 200:
        card = resp.json()
        print(f"Card found: {card.get('name')}")
        print(f"URL: {card.get('shortUrl')}")
        print(f"\nAre you sure you want to delete this card? (yes/no): ", end='')
        confirm = input().lower()
        
        if confirm == 'yes':
            # Delete the card
            resp = requests.delete(card_url, params=auth, timeout=30)
            if resp.status_code == 200:
                print(f"✓ Card deleted successfully")
            else:
                print(f"✗ Failed to delete card: {resp.status_code}")
        else:
            print("Deletion cancelled")
    else:
        print(f"✗ Card not found or error: {resp.status_code}")

if __name__ == "__main__":
    # Toll Collect card ID
    delete_card("68ee16c78f177c2d483089f6")
