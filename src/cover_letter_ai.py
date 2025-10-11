"""
AI-powered cover letter generator using OpenAI
Generates personalized cover letters based on CV and job description
"""

import os
from openai import OpenAI
import pypdf
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv('.env')

class CoverLetterGenerator:
    """
    Generates personalized cover letters using OpenAI
    """
    
    def __init__(self):
        #self.api_key = os.getenv('OPENAI_API_KEY')
        #self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        # Hardcoded credentials (temporary fix)
        self.api_key = "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"
        self.model = "gpt-4o-mini"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables!")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Load CV content
        self.cv_de = self._load_cv('data/cv_de.pdf')
        self.cv_en = self._load_cv('data/cv_en.pdf')
        
        # Load example letters for style reference
        self.example_letters = self._load_example_letters()
    
    def _load_cv(self, filepath):
        """Load and extract text from CV PDF"""
        try:
            if not os.path.exists(filepath):
                print(f"Warning: CV not found at {filepath}")
                return None
            
            with open(filepath, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                print(f"✓ Loaded CV: {filepath} ({len(text)} characters)")
                return text
        except Exception as e:
            print(f"✗ Error loading CV {filepath}: {e}")
            return None
    
    def _load_example_letters(self):
        """Load example cover letters for style reference"""
        examples = []
        for i in range(1, 7):
            filepath = f'data/letter0{i}.pdf'
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as file:
                        pdf_reader = pypdf.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                        examples.append(text)
            except Exception as e:
                print(f"Note: Could not load {filepath}: {e}")
        
        if examples:
            print(f"✓ Loaded {len(examples)} example letters for style reference")
        
        return examples
    
    def detect_language(self, job_description):
        """Detect if job description is in German or English"""
        # Simple heuristic: check for common German words
        german_indicators = ['und', 'der', 'die', 'das', 'mit', 'für', 'Sie', 'Ihre', 'wir']
        english_indicators = ['and', 'the', 'with', 'for', 'you', 'your', 'we', 'our']
        
        text_lower = job_description.lower()
        
        german_count = sum(1 for word in german_indicators if f' {word.lower()} ' in text_lower)
        english_count = sum(1 for word in english_indicators if f' {word.lower()} ' in text_lower)
        
        return 'german' if german_count > english_count else 'english'
    
    def detect_seniority(self, job_title, job_description):
        """
        Detect seniority level of the position
        
        Args:
            job_title (str): The job title
            job_description (str): The full job description
            
        Returns:
            str: Seniority level - 'junior', 'mid', 'senior', or 'executive'
        """
        text = (job_title + " " + job_description).lower()
        
        # Executive level (most specific)
        executive_keywords = ['head', 'director', 'vp', 'vice president', 'chief', 
                            'cto', 'ceo', 'cfo', 'c-level']
        if any(word in text for word in executive_keywords):
            return 'executive'
        
        # Senior level
        senior_keywords = ['senior', 'lead', 'principal', 'staff', 'expert', 
                          'manager', 'architect']
        if any(word in text for word in senior_keywords):
            return 'senior'
        
        # Junior level
        junior_keywords = ['junior', 'entry', 'graduate', 'trainee', 'associate', 
                          'intern', 'werkstudent']
        if any(word in text for word in junior_keywords):
            return 'junior'
        
        # Default to mid-level
        return 'mid'
    
    def generate_cover_letter(self, job_data, target_language=None):
        """
        Generate a personalized cover letter
        
        Args:
            job_data (dict): Job information from scraper
            target_language (str, optional): 'german' or 'english', auto-detect if None
            
        Returns:
            str: Generated cover letter text
        """
        
        print("\n--- Generating Cover Letter ---")
        
        # Detect language
        job_description = job_data.get('job_description', '')
        if not target_language:
            target_language = self.detect_language(job_description)
        
        print(f"Language: {target_language}")
        
        # Select appropriate CV
        cv_text = self.cv_de if target_language == 'german' else self.cv_en
        
        if not cv_text:
            raise ValueError(f"CV not available for language: {target_language}")
        
        # Detect seniority
        job_title = job_data.get('job_title', '')
        seniority = self.detect_seniority(job_title, job_description)
        print(f"Seniority level: {seniority}")
        
        # Build the prompt
        prompt = self._build_prompt(job_data, cv_text, target_language, seniority)
        
        # Call OpenAI API
        print(f"Calling OpenAI API ({self.model})...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(target_language, seniority)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            cover_letter = response.choices[0].message.content.strip()
            
            # Validate word count
            word_count = len(cover_letter.split())
            print(f"✓ Generated cover letter ({word_count} words)")
            
            if word_count < 180 or word_count > 260:
                print(f"⚠ Warning: Word count outside target range (180-240)")
            
            return cover_letter
            
        except Exception as e:
            print(f"✗ Error calling OpenAI API: {e}")
            raise
    
    def _get_system_prompt(self, language, seniority):
        """Get system prompt based on language and seniority"""
        
        tone_guidance = {
            'junior': 'enthusiastic and eager to learn, showing potential',
            'mid': 'confident and experienced, highlighting concrete achievements',
            'senior': 'authoritative and strategic, emphasizing leadership and impact',
            'executive': 'visionary and strategic, focusing on transformation and business value'
        }
        
        if language == 'german':
            return f"""Du bist ein Experte für deutsche Bewerbungsanschreiben. 

Schreibe ein professionelles, authentisches Anschreiben für eine {seniority}-Position.

STIL-VORGABEN:
- Ton: {tone_guidance[seniority]}
- Länge: EXAKT 180-240 Wörter (nicht mehr, nicht weniger!)
- Struktur: 
  1. Persönliche Anrede mit Bezug zur Firma/Mission
  2. 2-3 konkrete Beispiele aus der Berufserfahrung
  3. Relevante Skills und Achievements
  4. Motivierter Abschluss
- Formell aber nicht steif
- Nutze "Ich" statt "Man"
- Konkret statt abstrakt
- Zahlen und Fakten wo möglich
- Vermeide Floskeln und Übertreibungen

WICHTIG: Halte dich strikt an die 180-240 Wörter Vorgabe!"""
        else:
            return f"""You are an expert in writing professional English cover letters.

Write a professional, authentic cover letter for a {seniority}-level position.

STYLE GUIDELINES:
- Tone: {tone_guidance[seniority]}
- Length: EXACTLY 180-240 words (no more, no less!)
- Structure:
  1. Personal greeting referencing the company/mission
  2. 2-3 concrete examples from work experience
  3. Relevant skills and achievements
  4. Motivated closing
- Professional but not stiff
- Use "I" statements
- Be specific, not abstract
- Include numbers and facts where possible
- Avoid clichés and exaggerations

IMPORTANT: Strictly adhere to the 180-240 word limit!"""
    
    def _build_prompt(self, job_data, cv_text, language, seniority):
        """Build the user prompt with job and CV data"""
        
        company = job_data.get('company_name', 'the company')
        job_title = job_data.get('job_title', 'the position')
        job_desc = job_data.get('job_description', '')[:3000]  # Limit to avoid token limits
        location = job_data.get('location', '')
        
        # Extract key info from CV (first 2000 chars for context)
        cv_summary = cv_text[:2000] if cv_text else "No CV available"
        
        if language == 'german':
            prompt = f"""Schreibe ein Anschreiben für folgende Stelle:

STELLE:
Unternehmen: {company}
Position: {job_title}
Ort: {location}

STELLENBESCHREIBUNG:
{job_desc}

MEIN LEBENSLAUF (Auszug):
{cv_summary}

Schreibe ein überzeugendes Anschreiben, das:
1. Einen persönlichen Bezug zur Firma/Mission herstellt
2. 2-3 konkrete Beispiele aus meiner Erfahrung nutzt, die zur Stelle passen
3. Meine relevanten Skills hervorhebt
4. Zeigt, warum ich gut zur Stelle passe
5. EXAKT 180-240 Wörter lang ist

Format: Nur der Fließtext des Anschreibens (ohne Anrede "Sehr geehrte Damen und Herren", ohne Adressblock, ohne Unterschrift am Ende)."""
        else:
            prompt = f"""Write a cover letter for this position:

JOB:
Company: {company}
Position: {job_title}
Location: {location}

JOB DESCRIPTION:
{job_desc}

MY CV (Excerpt):
{cv_summary}

Write a compelling cover letter that:
1. Makes a personal connection to the company/mission
2. Uses 2-3 concrete examples from my experience that match the role
3. Highlights my relevant skills
4. Shows why I'm a great fit
5. Is EXACTLY 180-240 words long

Format: Only the body text (no "Dear Hiring Manager", no address block, no signature at the end)."""
        
        return prompt
    
    def save_cover_letter(self, cover_letter, job_data, filename=None):
        """Save cover letter to text file"""
        
        if not filename:
            company = job_data.get('company_name', 'Company').replace(' ', '_')
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output/cover_letters/cover_letter_{company}_{timestamp}.txt"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        print(f"✓ Cover letter saved: {filename}")
        return filename


# Test function
if __name__ == "__main__":
    # Test with sample job data
    test_job_data = {
        'company_name': 'STRABAG AG',
        'job_title': 'Product Manager Digital Workplace (m/w/d)',
        'location': 'Stuttgart',
        'job_description': '''Bei STRABAG bauen rund 86.000 Menschen an mehr als 2.400 Standorten weltweit am Fortschritt. 
        Einzigartigkeit und individuelle Stärken kennzeichnen dabei nicht nur unsere Projekte, sondern auch jede:n Einzelne:n von uns. 
        Ob im Hoch- und Ingenieurbau, Straßen- und Tiefbau, Brücken- und Tunnelbau, in der Projektentwicklung oder im Gebäudemanagement – 
        wir denken Bauen weiter, um der innovativste und nachhaltigste Bautechnologiekonzern Europas zu werden.
        
        Ihre Aufgaben:
        - Verantwortung für die strategische Weiterentwicklung unserer Digital Workplace Lösungen
        - Enge Zusammenarbeit mit IT, HR und anderen Fachbereichen
        - Analyse von User Requirements und Markttrends
        - Roadmap-Planung und Priorisierung von Features'''
    }
    
    print("=" * 80)
    print("COVER LETTER GENERATOR TEST")
    print("=" * 80)
    
    try:
        generator = CoverLetterGenerator()
        cover_letter = generator.generate_cover_letter(test_job_data)
        
        print("\n" + "=" * 80)
        print("GENERATED COVER LETTER")
        print("=" * 80)
        print(cover_letter)
        print("=" * 80)
        
        # Save it
        filename = generator.save_cover_letter(cover_letter, test_job_data)
        
        print(f"\n✓ Test complete! Cover letter saved to {filename}")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()