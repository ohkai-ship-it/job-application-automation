#!/usr/bin/env python3
"""Debug the Quelle field - check all related values."""

import sys
sys.path.insert(0, 'src')

from utils.env import load_env, get_str
import requests

load_env()

print("=" * 80)
print("DEBUGGING: Quelle (Source) Field Setting")
print("=" * 80)

# Config values
trello_key = get_str('TRELLO_KEY')
trello_token = get_str('TRELLO_TOKEN')
field_source_list = get_str('TRELLO_FIELD_QUELLE', default='')
field_source_linkedin = get_str('TRELLO_FIELD_QUELLE_LINKEDIN', default='')
field_source_stepstone = get_str('TRELLO_FIELD_QUELLE_STEPSTONE', default='')

print(f"\n📋 Configuration Values:")
print(f"  TRELLO_FIELD_QUELLE: {field_source_list}")
print(f"  TRELLO_FIELD_QUELLE_LINKEDIN: {field_source_linkedin}")
print(f"  TRELLO_FIELD_QUELLE_STEPSTONE: {field_source_stepstone}")

# Check if values are present
if not field_source_list:
    print("\n❌ ERROR: TRELLO_FIELD_QUELLE is not configured!")
    sys.exit(1)

if not field_source_linkedin:
    print("\n❌ ERROR: TRELLO_FIELD_QUELLE_LINKEDIN is not configured!")
    sys.exit(1)

# Card info
card_id = '68f15fe0f02fbd007648a324'
source_url = 'https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4311106890'

print(f"\n📍 Card Being Checked:")
print(f"  Card ID: {card_id}")
print(f"  Source URL: {source_url}")
print(f"  'linkedin' in URL: {'linkedin' in source_url.lower()}")

# Get current field value
print(f"\n🔍 Current Quelle Field Value:")
auth_params = {'key': trello_key, 'token': trello_token}

try:
    url_field = f"https://api.trello.com/1/cards/{card_id}/customFieldItems"
    response = requests.get(url_field, params=auth_params, timeout=5)
    fields = response.json()
    
    quelle_field = None
    for field in fields:
        if field.get('idCustomField') == field_source_list:
            quelle_field = field
            break
    
    if quelle_field:
        value = quelle_field.get('value', {})
        print(f"  Quelle Field Found!")
        print(f"  Current idValue: {value.get('idValue', 'NOT SET')}")
        print(f"  Expected idValue: {field_source_linkedin}")
        
        if value.get('idValue') == field_source_linkedin:
            print(f"  ✅ Value is CORRECT (set to LinkedIn)")
        else:
            print(f"  ❌ Value is WRONG (not set to LinkedIn)")
    else:
        print(f"  ❌ Quelle Field NOT FOUND on card!")
        print(f"\n  Available custom fields:")
        for field in fields:
            fid = field.get('idCustomField')
            val = field.get('value', {})
            if 'text' in val:
                print(f"    {fid}: {val['text']}")
            else:
                print(f"    {fid}: {val}")
    
except Exception as e:
    print(f"  ❌ Error fetching field: {e}")
    import traceback
    traceback.print_exc()
