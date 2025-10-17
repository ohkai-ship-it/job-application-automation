"""
Test the location logic for WERTGARANTIE job
"""
import sys
sys.path.insert(0, 'src')

from trello_connect import TrelloConnect

# Simulate WERTGARANTIE job data
job_data = {
    'company_name': 'WERTGARANTIE Group',
    'job_title': 'Product Owner (m/w/d) TechManager App',
    'location': 'Hannover',
    'work_mode': 'hybrid',
    'language': 'DE',
}

print("Testing location logic:")
print(f"Location: {job_data['location']}")
print(f"Work mode: {job_data['work_mode']}")

work_mode = (job_data.get('work_mode') or '').lower()
location = job_data.get('location', 'Düsseldorf')

print(f"\nProcessing:")
print(f"  work_mode (lower): '{work_mode}'")
print(f"  location: '{location}'")

# Determine what location to set
location_name = None
if work_mode == 'remote':
    location_name = 'Germany'
    print(f"  → Remote job: setting to 'Germany'")
elif 'düsseldorf' not in location.lower():
    location_name = location.split(',')[0].strip()
    print(f"  → Non-Düsseldorf: setting to '{location_name}'")
else:
    print(f"  → Düsseldorf: keeping default (not setting)")

print(f"\nFinal location_name to set: {location_name}")

# Now test actual API call
if location_name:
    print(f"\nWould call API to set location to: {location_name}")
    
    # Actually try it on the WERTGARANTIE card
    trello = TrelloConnect()
    card_id = "68ee3abe7cc543a94737df78"  # From the logs
    
    print(f"\nAttempting to set location on card {card_id}...")
    trello._set_card_location(card_id, job_data)
    
    print("\nCheck the card now: https://trello.com/c/5mP6h8xI")
