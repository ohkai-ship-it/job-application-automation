"""
Test OpenAI Cover Letter Generation
Quick test script to verify OpenAI integration works
"""

from dotenv import load_dotenv
load_dotenv('config/.env')

import sys
sys.path.append('src')

from cover_letter import CoverLetterGenerator

# Test job data (German)
job_data_de = {
    'company_name': 'ACME Technologies GmbH',
    'job_title': 'Senior Product Manager (m/w/d)',
    'job_description': '''Wir suchen einen erfahrenen Product Manager mit mindestens 5 Jahren 
    Erfahrung in der digitalen Produktentwicklung. Sie werden unser B2B-Portfolio strategisch 
    weiterentwickeln und cross-funktionale Teams leiten. Ihre Aufgaben umfassen die Roadmap-Planung, 
    Stakeholder-Management und die Kommerzialisierung neuer Produkte.'''
}

# Test job data (English)
job_data_en = {
    'company_name': 'TechStart Inc.',
    'job_title': 'Senior Software Engineer',
    'job_description': '''We are looking for an experienced Senior Software Engineer with strong 
    Python and cloud infrastructure expertise. You will lead backend development initiatives and 
    mentor junior developers in an agile environment.'''
}

def test_german_cover_letter():
    print("=" * 80)
    print("TEST 1: German Cover Letter Generation")
    print("=" * 80)
    
    gen = CoverLetterGenerator()
    
    print(f"\nJob: {job_data_de['job_title']}")
    print(f"Company: {job_data_de['company_name']}")
    print(f"\nGenerating cover letter...")
    
    try:
        letter = gen.generate_cover_letter(job_data_de)
        
        # Get the parts from job_data (populated by generate_cover_letter)
        salutation = job_data_de.get('cover_letter_salutation', '')
        body = job_data_de.get('cover_letter_body', letter)
        valediction = job_data_de.get('cover_letter_valediction', '')
        
        print("\n" + "=" * 80)
        print("GENERATED COVER LETTER (German)")
        print("=" * 80)
        print(f"\nSalutation: {salutation}")
        print(f"Body length: {len(body)} characters, {len(body.split())} words")
        print(f"Valediction: {valediction}")
        print("\n" + "-" * 80)
        print("FULL TEXT:")
        print("-" * 80)
        print(f"{salutation}\n\n{body}\n\n{valediction}")
        print("-" * 80)
        
        # Validate
        word_count = len(body.split())
        if 180 <= word_count <= 240:
            print(f"\n✅ Word count valid: {word_count} (target: 180-240)")
        else:
            print(f"\n⚠️  Word count: {word_count} (target: 180-240)")
        
        print("✅ German generation successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_english_cover_letter():
    print("=" * 80)
    print("TEST 2: English Cover Letter Generation")
    print("=" * 80)
    
    gen = CoverLetterGenerator()
    
    print(f"\nJob: {job_data_en['job_title']}")
    print(f"Company: {job_data_en['company_name']}")
    print(f"\nGenerating cover letter...")
    
    try:
        letter = gen.generate_cover_letter(job_data_en)
        
        # Get the parts from job_data
        salutation = job_data_en.get('cover_letter_salutation', '')
        body = job_data_en.get('cover_letter_body', letter)
        valediction = job_data_en.get('cover_letter_valediction', '')
        
        print("\n" + "=" * 80)
        print("GENERATED COVER LETTER (English)")
        print("=" * 80)
        print(f"\nSalutation: {salutation}")
        print(f"Body length: {len(body)} characters, {len(body.split())} words")
        print(f"Valediction: {valediction}")
        print("\n" + "-" * 80)
        print("PREVIEW (first 300 chars):")
        print("-" * 80)
        print(body[:300] + "...")
        print("-" * 80)
        
        # Validate
        word_count = len(body.split())
        if 180 <= word_count <= 240:
            print(f"\n✅ Word count valid: {word_count} (target: 180-240)")
        else:
            print(f"\n⚠️  Word count: {word_count} (target: 180-240)")
        
        print("✅ English generation successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("OPENAI COVER LETTER GENERATION TEST")
    print("=" * 80)
    print("\nThis will test cover letter generation with OpenAI API")
    print("Testing both German and English languages\n")
    
    # Run tests
    test1_pass = test_german_cover_letter()
    test2_pass = test_english_cover_letter()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"German generation: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"English generation: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    
    if test1_pass and test2_pass:
        print("\n🎉 All tests passed! OpenAI integration working correctly.")
        print("\nNext: Test full workflow (scrape → Trello → cover letter → DOCX)")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
