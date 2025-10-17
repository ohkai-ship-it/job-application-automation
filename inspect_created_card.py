#!/usr/bin/env python3
"""Inspect the created card's custom fields and attachments."""

import sys
import os
sys.path.insert(0, 'src')

from utils.env import load_env, get_str
import requests

load_env()

trello_key = get_str('TRELLO_KEY')
trello_token = get_str('TRELLO_TOKEN')
card_id = '68f15fe0f02fbd007648a324'  # The card we just created

print(f"Inspecting Trello card: {card_id}\n")
print("=" * 80)

auth_params = {'key': trello_key, 'token': trello_token}

# Get custom fields
print("\n📋 CUSTOM FIELDS:")
try:
    url_fields = f"https://api.trello.com/1/cards/{card_id}/customFieldItems"
    response = requests.get(url_fields, params=auth_params, timeout=5)
    fields = response.json()
    
    if fields:
        for field in fields:
            field_id = field.get('idCustomField')
            value = field.get('value', {})
            
            # Try to figure out what this field is
            if 'text' in value:
                print(f"  Field {field_id}: '{value.get('text')}'")
            elif 'idValue' in value:
                print(f"  Field {field_id} (option): {value.get('idValue')}")
            else:
                print(f"  Field {field_id}: {value}")
    else:
        print("  No custom fields set!")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Get attachments
print("\n🔗 ATTACHMENTS:")
try:
    url_attach = f"https://api.trello.com/1/cards/{card_id}/attachments"
    response = requests.get(url_attach, params=auth_params, timeout=5)
    attachments = response.json()
    
    if attachments:
        for i, attach in enumerate(attachments, 1):
            print(f"  {i}. {attach.get('name', 'N/A')}")
            print(f"     URL: {attach.get('url', 'N/A')}")
    else:
        print("  No attachments!")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Get board to find field IDs for reference
print("\n🔍 FIELD ID REFERENCE (from config):")
print(f"  TRELLO_FIELD_QUELLE: {get_str('TRELLO_FIELD_QUELLE')}")
print(f"  TRELLO_FIELD_QUELLE_LINKEDIN: {get_str('TRELLO_FIELD_QUELLE_LINKEDIN')}")
print(f"  TRELLO_FIELD_QUELLE_STEPSTONE: {get_str('TRELLO_FIELD_QUELLE_STEPSTONE')}")

print("\n" + "=" * 80)
print(f"\n🌐 View card at: https://trello.com/c/XS8tWLvY")
