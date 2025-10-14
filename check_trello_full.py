"""
Script to check all Trello board labels and custom fields including Sprache
"""
import sys
sys.path.insert(0, 'src')

import requests
from utils.env import load_env, get_str
from utils.trello import TRELLO_API_BASE, get_auth_params

def check_board():
    load_env()
    
    auth = get_auth_params()
    board_id = get_str('TRELLO_BOARD_ID')
    
    print("=" * 80)
    print("TRELLO BOARD LABELS")
    print("=" * 80)
    
    # Get all labels
    labels_url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
    resp = requests.get(labels_url, params=auth, timeout=30)
    
    if resp.status_code == 200:
        labels = resp.json()
        
        # Group labels by name keywords
        work_mode_labels = []
        language_labels = []
        seniority_labels = []
        location_labels = []
        other_labels = []
        
        for label in labels:
            name = label['name']
            label_id = label['id']
            color = label.get('color', 'none')
            
            name_lower = name.lower()
            
            if 'remote' in name_lower or 'hybrid' in name_lower or 'onsite' in name_lower or 'office' in name_lower:
                work_mode_labels.append((name, label_id, color))
            elif name_lower in ['de', 'en', 'german', 'english', 'deutsch', 'englisch']:
                language_labels.append((name, label_id, color))
            elif any(x in name_lower for x in ['junior', 'mid', 'senior', 'lead', 'principal']):
                seniority_labels.append((name, label_id, color))
            elif 'ddd' in name_lower or 'düsseldorf' in name_lower:
                location_labels.append((name, label_id, color))
            else:
                other_labels.append((name, label_id, color))
        
        def print_labels(category, labels_list):
            print(f"\n{category}:")
            if labels_list:
                for name, label_id, color in labels_list:
                    print(f"  {name:30} | ID: {label_id} | Color: {color}")
            else:
                print("  (none found)")
        
        print_labels("WORK MODE LABELS", work_mode_labels)
        print_labels("LANGUAGE LABELS", language_labels)
        print_labels("SENIORITY LABELS", seniority_labels)
        print_labels("LOCATION LABELS (DDD)", location_labels)
        print_labels("OTHER LABELS", other_labels)
    else:
        print(f"✗ Failed to fetch labels: {resp.status_code}")
    
    print("\n" + "=" * 80)
    print("TRELLO BOARD CUSTOM FIELDS")
    print("=" * 80)
    
    # Get all custom fields
    fields_url = f"{TRELLO_API_BASE}/boards/{board_id}/customFields"
    resp = requests.get(fields_url, params=auth, timeout=30)
    
    if resp.status_code == 200:
        fields = resp.json()
        
        for field in fields:
            field_name = field['name']
            field_id = field['id']
            field_type = field['type']
            
            print(f"\n{field_name}")
            print(f"  ID: {field_id}")
            print(f"  Type: {field_type}")
            
            # If it's a list/dropdown, show options
            if field_type == 'list' and 'options' in field:
                print("  Options:")
                for opt in field['options']:
                    opt_name = opt['value']['text']
                    opt_id = opt['id']
                    print(f"    - {opt_name}: {opt_id}")
    else:
        print(f"✗ Failed to fetch custom fields: {resp.status_code}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_board()
