import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables (try both locations)
load_dotenv('config/credentials.env')

# Try both naming conventions
TRELLO_KEY = os.getenv('TRELLO_KEY') or os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN') or os.getenv('TRELLO_API_TOKEN')
BOARD_ID = os.getenv('TRELLO_BOARD_ID')
TEMPLATE_CARD_ID = os.getenv('TRELLO_TEMPLATE_CARD_ID')

print(f"Key: {TRELLO_KEY}")
print(f"Token: {TRELLO_TOKEN}")
# Paste your credentials directly here for testing
TRELLO_KEY = "0e7aa288ad7ee04d6bc72481cc071579"
TRELLO_TOKEN = "ATTAb139469c8e9ad52ad7183c812b7ed69b29399040b3867cc058a3332f99913b60520DDEAD"

print(f"Debug - Key loaded: {TRELLO_KEY is not None}")
print(f"Debug - Token loaded: {TRELLO_TOKEN is not None}")
print(f"Debug - Board ID loaded: {BOARD_ID is not None}")

def inspect_trello_board():
    """
    Inspects the Trello board to understand its structure
    """
    
    print("=" * 80)
    print("TRELLO BOARD INSPECTOR")
    print("=" * 80)
    
    # Check credentials
    if not TRELLO_KEY or not TRELLO_TOKEN:
        print("✗ Error: Missing Trello credentials!")
        print("Make sure TRELLO_KEY and TRELLO_TOKEN are set in .env or config/credentials.env")
        return
    
    print(f"\n✓ API Key: {TRELLO_KEY[:10]}...")
    print(f"✓ Token: {TRELLO_TOKEN[:10]}...")
    print(f"✓ Board ID: {BOARD_ID}")
    
    base_url = "https://api.trello.com/1"
    auth_params = {
        'key': TRELLO_KEY,
        'token': TRELLO_TOKEN
    }
    
    try:
        # 1. Get Board Info
        print("\n" + "-" * 80)
        print("BOARD INFORMATION")
        print("-" * 80)
        
        board_url = f"{base_url}/boards/{BOARD_ID}"
        response = requests.get(board_url, params=auth_params)
        response.raise_for_status()
        board = response.json()
        
        print(f"\nBoard Name: {board['name']}")
        print(f"Board URL: {board['url']}")
        print(f"Description: {board.get('desc', 'No description')}")
        
        # 2. Get Lists
        print("\n" + "-" * 80)
        print("LISTS ON BOARD")
        print("-" * 80)
        
        lists_url = f"{base_url}/boards/{BOARD_ID}/lists"
        response = requests.get(lists_url, params=auth_params)
        response.raise_for_status()
        lists = response.json()
        
        print(f"\nFound {len(lists)} lists:\n")
        for i, list_item in enumerate(lists, 1):
            print(f"{i}. {list_item['name']}")
            print(f"   ID: {list_item['id']}")
            print(f"   Position: {list_item['pos']}")
            print()
        
        # 3. Get Custom Fields
        print("-" * 80)
        print("CUSTOM FIELDS")
        print("-" * 80)
        
        fields_url = f"{base_url}/boards/{BOARD_ID}/customFields"
        response = requests.get(fields_url, params=auth_params)
        
        if response.status_code == 200:
            custom_fields = response.json()
            if custom_fields:
                print(f"\nFound {len(custom_fields)} custom fields:\n")
                for i, field in enumerate(custom_fields, 1):
                    print(f"{i}. {field['name']}")
                    print(f"   ID: {field['id']}")
                    print(f"   Type: {field['type']}")
                    if field['type'] == 'list' and 'options' in field:
                        print(f"   Options: {[opt['value']['text'] for opt in field['options']]}")
                    print()
            else:
                print("\nNo custom fields found on this board.")
        else:
            print("\nCouldn't retrieve custom fields (may require Power-Up enabled)")
        
        # 4. Get Template Card Info
        if TEMPLATE_CARD_ID:
            print("-" * 80)
            print("TEMPLATE CARD")
            print("-" * 80)
            
            card_url = f"{base_url}/cards/{TEMPLATE_CARD_ID}"
            response = requests.get(card_url, params=auth_params)
            
            if response.status_code == 200:
                template = response.json()
                print(f"\nTemplate Name: {template['name']}")
                print(f"Description: {template['desc'][:200]}..." if len(template['desc']) > 200 else f"Description: {template['desc']}")
                print(f"List: {template['idList']}")
                print(f"Labels: {[label['name'] for label in template.get('labels', [])]}")
                
                # Get checklists
                checklists_url = f"{base_url}/cards/{TEMPLATE_CARD_ID}/checklists"
                response = requests.get(checklists_url, params=auth_params)
                if response.status_code == 200:
                    checklists = response.json()
                    if checklists:
                        print(f"\nChecklists ({len(checklists)}):")
                        for checklist in checklists:
                            print(f"  - {checklist['name']}: {len(checklist['checkItems'])} items")
                
                # Get custom field values
                customfield_url = f"{base_url}/cards/{TEMPLATE_CARD_ID}/customFieldItems"
                response = requests.get(customfield_url, params=auth_params)
                if response.status_code == 200:
                    custom_values = response.json()
                    if custom_values:
                        print(f"\nCustom Fields Set: {len(custom_values)}")
            else:
                print(f"\n✗ Could not retrieve template card (Status: {response.status_code})")
        
        # 5. Get Labels
        print("\n" + "-" * 80)
        print("LABELS")
        print("-" * 80)
        
        labels_url = f"{base_url}/boards/{BOARD_ID}/labels"
        response = requests.get(labels_url, params=auth_params)
        response.raise_for_status()
        labels = response.json()
        
        if labels:
            print(f"\nFound {len(labels)} labels:\n")
            for label in labels:
                name = label['name'] if label['name'] else '(No name)'
                print(f"  - {name} (Color: {label['color']}, ID: {label['id']})")
        else:
            print("\nNo labels found on this board.")
        
        print("\n" + "=" * 80)
        print("INSPECTION COMPLETE")
        print("=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error connecting to Trello: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    inspect_trello_board()