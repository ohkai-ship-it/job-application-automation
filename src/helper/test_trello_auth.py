import requests

from src.utils.env import load_env
from src.utils.trello import get_auth_params, mask_secret, TRELLO_API_BASE

load_env()

print("Testing Trello API connection...")
auth = get_auth_params()
key = auth.get('key', '')
token = auth.get('token', '')
print(f"Key: {mask_secret(key, 10)}")
print(f"Token: {mask_secret(token, 10)}")

if not key or not token:
    print("✗ Missing key/token. Please set TRELLO_KEY and TRELLO_TOKEN in config/.env")
else:
    # Test 1: Check if we can authenticate
    url = f"{TRELLO_API_BASE}/members/me"
    response = requests.get(url, params=auth)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Logged in as: {data['fullName']}")
        print(f"✓ Username: {data['username']}")
    else:
        print("✗ Failed!")
        print(f"Response: {response.text}")