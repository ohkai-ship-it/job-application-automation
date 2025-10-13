"""
Script to generate .env entries for Trello custom fields based on actual board configuration.
Run this to get the field IDs you need to add to config/.env
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def generate_env_config():
    load_env()
    
    auth = get_auth_params()
    board_id = get_str('TRELLO_BOARD_ID')
    
    # Get board custom fields
    fields_url = f"{TRELLO_API_BASE}/boards/{board_id}/customFields"
    resp = requests.get(fields_url, params=auth, timeout=30)
    
    if resp.status_code != 200:
        print(f"✗ Failed to fetch custom fields: {resp.status_code}")
        return
    
    fields = resp.json()
    
    print("=" * 70)
    print("TRELLO CUSTOM FIELD CONFIGURATION FOR .env")
    print("=" * 70)
    print("\n# Add these to your config/.env file:\n")
    
    # Map field names to env var names
    field_mapping = {
        'Firmenname': 'TRELLO_FIELD_FIRMENNAME',
        'Rollentitel': 'TRELLO_FIELD_ROLLENTITEL',
        'Quelle': 'TRELLO_FIELD_QUELLE',
        'Ausschreibungsdatum': 'TRELLO_FIELD_AUSSCHREIBUNGSDATUM',
        'Firma - Person': 'TRELLO_FIELD_FIRMA_PERSON',
    }
    
    for field in fields:
        field_name = field['name']
        field_id = field['id']
        field_type = field['type']
        
        if field_name in field_mapping:
            env_var = field_mapping[field_name]
            print(f"{env_var}={field_id}")
            
            # If it's a list type, also show option IDs
            if field_type == 'list' and 'options' in field:
                print(f"# {field_name} options:")
                for opt in field['options']:
                    opt_name = opt['value']['text']
                    opt_id = opt['id']
                    # Create env var for Stepstone option
                    if field_name == 'Quelle' and opt_name == 'Stepstone':
                        print(f"TRELLO_FIELD_QUELLE_STEPSTONE={opt_id}")
                    print(f"#   - {opt_name}: {opt_id}")
            print()
    
    print("=" * 70)
    print("\nCopy the above lines to your config/.env file")
    print("=" * 70)

if __name__ == "__main__":
    generate_env_config()
