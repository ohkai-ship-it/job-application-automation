import requests

# Paste your credentials directly here for testing
TRELLO_KEY = "0e7aa288ad7ee04d6bc72481cc071579"
TRELLO_TOKEN = "ATTAb139469c8e9ad52ad7183c812b7ed69b29399040b3867cc058a3332f99913b60520DDEAD"

print("Testing Trello API connection...")
print(f"Key: {TRELLO_KEY[:10]}...")
print(f"Token: {TRELLO_TOKEN[:10]}...")

# Test 1: Check if we can authenticate
url = "https://api.trello.com/1/members/me"
params = {
    'key': TRELLO_KEY,
    'token': TRELLO_TOKEN
}

response = requests.get(url, params=params)
print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✓ Success! Logged in as: {data['fullName']}")
    print(f"✓ Username: {data['username']}")
else:
    print(f"✗ Failed!")
    print(f"Response: {response.text}")