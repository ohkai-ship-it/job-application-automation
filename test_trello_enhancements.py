"""
Test script to verify Trello card enhancements:
1. Labels: Work mode + DDD for Düsseldorf
2. Description: Only job description text
3. Location: Map based on job location/work mode
4. Custom field: Sprache (DE -> DE or EN -> EN)
5. Attachments: Stepstone link + career page
"""
import sys
sys.path.insert(0, 'src')

from trello_connect import TrelloConnect

# Test data: Düsseldorf location (should get DDD label)
test_job_dusseldorf = {
    'company_name': 'Test Company GmbH',
    'job_title': 'Senior Python Developer',
    'job_title_clean': 'Senior Python Developer',
    'location': 'Düsseldorf, NRW, DE',
    'work_mode': 'hybrid',
    'language': 'DE',
    'seniority': 'senior',
    'job_description': '''Dies ist eine vollständige Stellenbeschreibung auf Deutsch.

Ihre Aufgaben:
- Entwicklung von Python-Anwendungen
- Code Reviews durchführen
- Team-Meetings leiten

Ihr Profil:
- 5+ Jahre Python-Erfahrung
- Sehr gute Deutschkenntnisse
- Teamfähigkeit

Wir bieten:
- Hybrides Arbeiten
- Attraktives Gehalt
- Weiterbildungsmöglichkeiten''',
    'source_url': 'https://www.stepstone.de/stellenangebote--Senior-Python-Developer-Test-Company-GmbH-Duesseldorf-12345678.html',
    'career_page_link': 'https://www.testcompany.de/karriere',
    'publication_date': '2025-10-14T10:00:00Z',
    'company_address_line1': 'Teststraße 123',
    'company_address_line2': '40211 Düsseldorf'
}

# Test data: Remote job (should get "Germany" location)
test_job_remote = {
    'company_name': 'Remote Corp',
    'job_title': 'DevOps Engineer',
    'job_title_clean': 'DevOps Engineer',
    'location': 'Remote, Germany',
    'work_mode': 'remote',
    'language': 'EN',
    'seniority': 'mid',
    'job_description': '''This is a complete English job description.

Your responsibilities:
- Deploy cloud infrastructure
- Monitor system performance
- Automate workflows

Your profile:
- 3+ years DevOps experience
- Strong English skills
- Self-motivated

What we offer:
- 100% remote work
- Competitive salary
- Professional development''',
    'source_url': 'https://www.stepstone.de/stellenangebote--DevOps-Engineer-Remote-Corp-Remote-87654321.html',
    'publication_date': '2025-10-14T12:00:00Z',
}

# Test data: Munich location (should get "München" location, no DDD)
test_job_munich = {
    'company_name': 'Munich Tech AG',
    'job_title': 'Full Stack Developer',
    'job_title_clean': 'Full Stack Developer',
    'location': 'München, Bayern, DE',
    'work_mode': 'onsite',
    'language': 'DE',
    'seniority': 'mid',
    'job_description': '''Vollständige Stellenbeschreibung für München.

Das erwartet Sie:
- Frontend und Backend Entwicklung
- Agile Teamarbeit
- Moderne Technologien

Das bringen Sie mit:
- JavaScript und Python Kenntnisse
- Deutschkenntnisse
- Leidenschaft für Coding

Unser Angebot:
- Vor-Ort in München
- Modernes Office
- Team-Events''',
    'source_url': 'https://www.stepstone.de/stellenangebote--Full-Stack-Developer-Munich-Tech-AG-Muenchen-11223344.html',
    'career_page_link': 'https://www.munichtech.de/jobs',
    'publication_date': '2025-10-14T14:00:00Z',
}

def test_card_creation(job_data: dict, test_name: str):
    """Test creating a Trello card with the given job data."""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)
    
    print(f"\nJob Data Summary:")
    print(f"  Company: {job_data['company_name']}")
    print(f"  Location: {job_data['location']}")
    print(f"  Work Mode: {job_data['work_mode']}")
    print(f"  Language: {job_data['language']}")
    print(f"  Source: {job_data['source_url']}")
    
    trello = TrelloConnect()
    result = trello.create_card_from_job_data(job_data)
    
    if result:
        print(f"\n✓ Card created successfully!")
        print(f"  URL: {result.get('shortUrl', 'N/A')}")
        print(f"\nExpected settings:")
        print(f"  Labels: Work mode ({job_data['work_mode']})" + 
              (", DDD" if 'düsseldorf' in job_data['location'].lower() else ""))
        print(f"  Description: Full job description ({len(job_data['job_description'])} chars)")
        
        location_expectation = "Germany" if job_data['work_mode'] == 'remote' else \
                             ("Düsseldorf (default)" if 'düsseldorf' in job_data['location'].lower() else 
                              job_data['location'].split(',')[0])
        print(f"  Location: {location_expectation}")
        
        sprache = f"{job_data['language']} -> {job_data['language']}"
        print(f"  Sprache field: {sprache}")
        
        print(f"  Attachments:")
        print(f"    - Ausschreibung: {job_data['source_url']}")
        if job_data.get('career_page_link'):
            print(f"    - Firmenportal: {job_data['career_page_link']}")
        else:
            print(f"    - Firmenportal: (none - template default)")
    else:
        print(f"\n✗ Failed to create card")
    
    return result

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TRELLO CARD ENHANCEMENTS TEST")
    print("=" * 80)
    print("\nThis will create 3 test cards to verify:")
    print("1. Düsseldorf job (hybrid) - should get DDD label")
    print("2. Remote job - should get 'Germany' location")
    print("3. Munich job (onsite) - should get 'München' location")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Run tests
    test_card_creation(test_job_dusseldorf, "Düsseldorf Hybrid Job")
    test_card_creation(test_job_remote, "Remote Job")
    test_card_creation(test_job_munich, "Munich Onsite Job")
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)
    print("\nPlease verify the following in your Trello board:")
    print("1. ✓ Labels show work mode (Remote/Hybrid/On-site)")
    print("2. ✓ Düsseldorf job has 'DDD' label")
    print("3. ✓ Description contains ONLY the job description text (no formatting)")
    print("4. ✓ Location map is set correctly:")
    print("   - Düsseldorf job: Düsseldorf")
    print("   - Remote job: Germany")
    print("   - Munich job: München")
    print("5. ✓ 'Sprache' custom field is set (DE -> DE or EN -> EN)")
    print("6. ✓ Attachments:")
    print("   - 'Ausschreibung' links to Stepstone")
    print("   - 'Firmenportal' links to career page (if available)")
    print("\n" + "=" * 80)
