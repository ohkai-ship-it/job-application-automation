"""
Simple script to delete all cards from the "Erforschen" list.
Run from project root: python delete_erforschen_cards.py
"""
import os
import sys
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def main():
    load_env()
    
    auth = get_auth_params()
    board_id = get_str('TRELLO_BOARD_ID')
    
    if not auth.get('key') or not auth.get('token'):
        print("✗ Missing Trello credentials")
        return 1
    
    if not board_id:
        print("✗ Missing TRELLO_BOARD_ID")
        return 1
    
    list_name = "Erforschen"
    print(f"Searching for list: '{list_name}'...")
    
    # Get all lists
    lists_url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
    resp = requests.get(lists_url, params=auth, timeout=30)
    
    if resp.status_code != 200:
        print(f"✗ Failed to fetch lists: {resp.status_code}")
        return 2
    
    lists = resp.json()
    target_list = None
    
    for lst in lists:
        if lst.get('name') == list_name:
            target_list = lst
            break
    
    if not target_list:
        print(f"✗ List '{list_name}' not found")
        print("\nAvailable lists:")
        for lst in lists:
            print(f"  - {lst.get('name')}")
        return 3
    
    list_id = target_list['id']
    print(f"✓ Found list: '{list_name}' (id={list_id})")
    
    # Get all cards
    cards_url = f"{TRELLO_API_BASE}/lists/{list_id}/cards"
    resp = requests.get(cards_url, params=auth, timeout=30)
    
    if resp.status_code != 200:
        print(f"✗ Failed to fetch cards: {resp.status_code}")
        return 4
    
    cards = resp.json()
    
    if not cards:
        print(f"✓ List is already empty")
        return 0
    
    print(f"\nFound {len(cards)} card(s):")
    for card in cards:
        print(f"  - {card.get('name')}")
    
    # Confirm
    print(f"\n⚠️  DELETE all {len(cards)} card(s)?")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("✗ Cancelled")
        return 0
    
    # Delete
    deleted = 0
    failed = 0
    
    print(f"\nDeleting...")
    for card in cards:
        card_id = card['id']
        card_name = card.get('name', 'Unnamed')
        
        delete_url = f"{TRELLO_API_BASE}/cards/{card_id}"
        resp = requests.delete(delete_url, params=auth, timeout=30)
        
        if resp.status_code == 200:
            deleted += 1
            print(f"  ✓ {card_name}")
        else:
            failed += 1
            print(f"  ✗ {card_name} (status {resp.status_code})")
    
    print(f"\n{'='*50}")
    print(f"Deleted: {deleted} | Failed: {failed}")
    print(f"{'='*50}")
    
    return 0 if failed == 0 else 5


if __name__ == "__main__":
    sys.exit(main())
