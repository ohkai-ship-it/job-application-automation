"""
Helper script to delete all cards from a specific Trello list.
Usage: python src/helper/delete_cards_from_list.py "List Name"
"""
import sys
import requests
from src.utils.env import load_env, get_str
from src.utils.trello import TRELLO_API_BASE, get_auth_params

def delete_cards_from_list(list_name: str) -> int:
    """
    Delete all cards from a specific Trello list by name.
    
    Args:
        list_name: Name of the list to clear
        
    Returns:
        Exit code (0 = success, non-zero = error)
    """
    load_env()
    
    auth = get_auth_params()
    board_id = get_str('TRELLO_BOARD_ID')
    
    if not auth.get('key') or not auth.get('token'):
        print("✗ Missing Trello credentials (TRELLO_KEY/TRELLO_TOKEN)")
        return 1
    
    if not board_id:
        print("✗ Missing TRELLO_BOARD_ID in environment")
        return 1
    
    print(f"Searching for list: '{list_name}'...")
    
    # Get all lists on the board
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
        print(f"✗ List '{list_name}' not found on board")
        print("\nAvailable lists:")
        for lst in lists:
            print(f"  - {lst.get('name')}")
        return 3
    
    list_id = target_list['id']
    print(f"✓ Found list: '{list_name}' (id={list_id})")
    
    # Get all cards in the list
    cards_url = f"{TRELLO_API_BASE}/lists/{list_id}/cards"
    resp = requests.get(cards_url, params=auth, timeout=30)
    
    if resp.status_code != 200:
        print(f"✗ Failed to fetch cards: {resp.status_code}")
        return 4
    
    cards = resp.json()
    
    if not cards:
        print(f"✓ List '{list_name}' is already empty (0 cards)")
        return 0
    
    print(f"\nFound {len(cards)} card(s) in list '{list_name}':")
    for card in cards:
        print(f"  - {card.get('name')}")
    
    # Ask for confirmation
    print(f"\n⚠️  This will DELETE all {len(cards)} card(s) from '{list_name}'")
    confirm = input("Type 'yes' to confirm deletion: ")
    
    if confirm.lower() != 'yes':
        print("✗ Deletion cancelled")
        return 0
    
    # Delete each card
    deleted_count = 0
    failed_count = 0
    
    print(f"\nDeleting {len(cards)} card(s)...")
    for card in cards:
        card_id = card['id']
        card_name = card.get('name', 'Unnamed')
        
        delete_url = f"{TRELLO_API_BASE}/cards/{card_id}"
        resp = requests.delete(delete_url, params=auth, timeout=30)
        
        if resp.status_code == 200:
            deleted_count += 1
            print(f"  ✓ Deleted: {card_name}")
        else:
            failed_count += 1
            print(f"  ✗ Failed to delete: {card_name} (status {resp.status_code})")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Deleted: {deleted_count}")
    print(f"  Failed:  {failed_count}")
    print(f"{'='*60}")
    
    return 0 if failed_count == 0 else 5


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/helper/delete_cards_from_list.py \"List Name\"")
        print("\nExample:")
        print("  python src/helper/delete_cards_from_list.py \"Erforschen\"")
        sys.exit(1)
    
    list_name = sys.argv[1]
    exit_code = delete_cards_from_list(list_name)
    sys.exit(exit_code)
