"""
Script to inspect a specific Trello card and its custom field values.
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def inspect_card(card_name: str):
    load_env()
    
    auth = get_auth_params()
    board_id = get_str('TRELLO_BOARD_ID')
    
    print(f"Searching for card: '{card_name}'...")
    
    # Get all lists on the board
    lists_url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
    resp = requests.get(lists_url, params=auth, timeout=30)
    lists = resp.json()
    
    # Find the card
    found_card = None
    for lst in lists:
        cards_url = f"{TRELLO_API_BASE}/lists/{lst['id']}/cards"
        resp = requests.get(cards_url, params=auth, timeout=30)
        cards = resp.json()
        
        for card in cards:
            if card_name.lower() in card.get('name', '').lower():
                found_card = card
                print(f"\n✓ Found card: {card['name']}")
                print(f"  List: {lst['name']}")
                print(f"  ID: {card['id']}")
                print(f"  URL: {card.get('shortUrl', 'N/A')}")
                break
        if found_card:
            break
    
    if not found_card:
        print(f"✗ Card not found")
        return
    
    # Get custom field values
    card_id = found_card['id']
    custom_fields_url = f"{TRELLO_API_BASE}/cards/{card_id}/customFieldItems"
    resp = requests.get(custom_fields_url, params=auth, timeout=30)
    
    if resp.status_code == 200:
        field_items = resp.json()
        
        # Get board custom fields to map IDs to names
        board_fields_url = f"{TRELLO_API_BASE}/boards/{board_id}/customFields"
        resp = requests.get(board_fields_url, params=auth, timeout=30)
        board_fields = resp.json()
        
        # Create field ID to name mapping
        field_map = {f['id']: f for f in board_fields}
        
        print(f"\n{'='*60}")
        print("CUSTOM FIELDS:")
        print(f"{'='*60}")
        
        if field_items:
            for item in field_items:
                field_id = item.get('idCustomField')
                field_info = field_map.get(field_id, {})
                field_name = field_info.get('name', 'Unknown')
                field_type = field_info.get('type', 'unknown')
                
                # Get value based on type
                value = 'N/A'
                if 'value' in item:
                    if field_type == 'text':
                        value = item['value'].get('text', 'N/A')
                    elif field_type == 'number':
                        value = item['value'].get('number', 'N/A')
                    elif field_type == 'date':
                        value = item['value'].get('date', 'N/A')
                    elif field_type == 'checkbox':
                        value = item['value'].get('checked', 'N/A')
                    elif field_type == 'list':
                        option_id = item.get('idValue')
                        # Find option text
                        for opt in field_info.get('options', []):
                            if opt['id'] == option_id:
                                value = opt['value']['text']
                                break
                
                print(f"{field_name:30} | Type: {field_type:10} | Value: {value}")
        else:
            print("No custom fields set on this card")
        
        print(f"{'='*60}")
        
        # Show board custom fields for reference
        print(f"\nAVAILABLE CUSTOM FIELDS ON BOARD:")
        print(f"{'='*60}")
        for field in board_fields:
            print(f"{field['name']:30} | Type: {field['type']:10} | ID: {field['id']}")
            if field['type'] == 'list' and 'options' in field:
                for opt in field['options']:
                    print(f"  - {opt['value']['text']} (id: {opt['id']})")
        print(f"{'='*60}")
    
    # Show labels
    print(f"\nLABELS:")
    print(f"{'='*60}")
    if found_card.get('labels'):
        for label in found_card['labels']:
            print(f"{label.get('name', '(No name)'):30} | Color: {label.get('color', 'N/A')}")
    else:
        print("No labels on this card")
    print(f"{'='*60}")
    
    # Show description preview
    print(f"\nDESCRIPTION PREVIEW:")
    print(f"{'='*60}")
    desc = found_card.get('desc', '')
    if desc:
        print(desc[:500] + ("..." if len(desc) > 500 else ""))
    else:
        print("No description")
    print(f"{'='*60}")

if __name__ == "__main__":
    card_name = "QIAGEN GmbH - AI Product Owner"
    inspect_card(card_name)
