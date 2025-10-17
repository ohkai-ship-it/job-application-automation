"""
Get details of Bewerbungsportal field
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import requests
from src.utils.env import load_env, get_str

load_env()

API_KEY = get_str('TRELLO_KEY')
TOKEN = get_str('TRELLO_TOKEN')

# Get Bewerbungsportal field details
field_id = '67adeccaf57fac30c53a61dd'  # Bewerbungsportal

url = f"https://api.trello.com/1/customFields/{field_id}"
params = {'key': API_KEY, 'token': TOKEN}

response = requests.get(url, params=params)
field = response.json()

print(f"Field: {field['name']}")
print(f"Type: {field['type']}")
print()

if field.get('options'):
    print("Available Options:")
    for i, opt in enumerate(field['options']):
        print(f"  {i+1}. {opt.get('value', opt.get('text', 'Unknown'))}")
        print(f"     ID: {opt.get('id')}")
        print()
