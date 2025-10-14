"""
cover_letter.py
Implements CoverLetterGenerator for AI-powered cover letter generation using OpenAI.
Loads CVs, builds prompts, detects language/seniority, and saves cover letters.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
try:
    from .utils.env import get_str
    from .utils.log_config import get_logger
    from .utils.errors import AIGenerationError
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.env import get_str
    from utils.log_config import get_logger
    from utils.errors import AIGenerationError
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    import pypdf
except ImportError:
    pypdf = None

class CoverLetterGenerator:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.api_key = get_str('OPENAI_API_KEY', default=None)
        if not self.api_key or self.api_key.strip() == '':
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.model = get_str('OPENAI_MODEL', default='gpt-4o-mini')
        self.client = OpenAI(api_key=self.api_key) if OpenAI else None
        self.cv_de = self._load_cv('data/cv_de.pdf')
        self.cv_en = self._load_cv('data/cv_en.pdf')

    def _load_cv(self, filepath: str) -> Optional[str]:
        if not pypdf or not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = "".join(page.extract_text() or '' for page in pdf_reader.pages)
                return text
        except Exception as e:
            self.logger.warning("Error loading CV %s: %s", filepath, e)
            return None

    def detect_language(self, job_description: str) -> str:
        german = sum(w in job_description.lower() for w in [' und ', ' der ', ' die ', ' das ', ' mit ', ' für '])
        english = sum(w in job_description.lower() for w in [' and ', ' the ', ' with ', ' for '])
        return 'german' if german > english else 'english'

    def detect_seniority(self, job_title: str, job_description: str) -> str:
        text = (job_title + ' ' + job_description).lower()
        if any(w in text for w in ['head', 'director', 'vp', 'chief', 'cto', 'ceo', 'cfo']):
            return 'executive'
        if any(w in text for w in ['senior', 'lead', 'principal', 'manager', 'architect']):
            return 'senior'
        if any(w in text for w in ['junior', 'entry', 'trainee', 'associate', 'intern', 'werkstudent']):
            return 'junior'
        return 'mid'
    
    def detect_german_formality(self, job_description: str) -> str:
        """
        Detect formality level in German job descriptions (du vs Sie).
        
        Args:
            job_description: The job description text
            
        Returns:
            'informal' if informal pronouns detected (du/dich/dir/dein)
            'formal' if formal pronouns detected (Sie/Ihnen/Ihr) or default
        """
        if not job_description:
            return 'formal'
        
        text_lower = job_description.lower()
        
        # Count informal pronouns (du-form)
        informal_pronouns = ['du ', ' du ', ' dich ', ' dir ', ' dein ', ' deine ', ' deinem ', ' deinen ', ' deiner ']
        informal_count = sum(1 for p in informal_pronouns if p in text_lower)
        
        # Count formal pronouns (Sie-form)
        # Be careful with 'sie' which can mean 'she/they' - look for capitalized context clues
        formal_pronouns = [' sie ', ' ihnen ', ' ihr ', ' ihre ', ' ihrem ', ' ihren ', ' ihrer ']
        formal_count = sum(1 for p in formal_pronouns if p in text_lower)
        
        # Also check for capitalized "Sie" which is more definitive
        if ' Sie ' in job_description or job_description.startswith('Sie '):
            formal_count += 3  # Weight capitalized Sie heavily
        
        # If informal pronouns found and significantly more than formal, it's informal
        if informal_count > 0 and informal_count > formal_count:
            self.logger.debug("Detected informal German (du-form): informal=%d, formal=%d", informal_count, formal_count)
            return 'informal'
        
        # Default to formal (professional standard)
        self.logger.debug("Using formal German (Sie-form): informal=%d, formal=%d", informal_count, formal_count)
        return 'formal'
    
    def generate_salutation(self, job_data: Dict[str, Any], language: str, formality: str, seniority: str) -> str:
        """
        Generate appropriate salutation based on available contact info and context.
        
        Args:
            job_data: Job data dictionary with potential contact_person info
            language: 'german' or 'english'
            formality: 'formal' or 'informal' (mainly for German)
            seniority: Seniority level for tone matching
            
        Returns:
            Appropriate salutation string
        """
        company_name = job_data.get('company_name', 'Team')
        contact_person = job_data.get('contact_person', {})
        contact_name = contact_person.get('name') if isinstance(contact_person, dict) else None
        
        # If we have a contact person name, use personalized greeting
        if contact_name and contact_name.strip():
            name_parts = contact_name.strip().split()
            
            if language == 'german':
                if formality == 'informal':
                    # Informal German: use first name
                    first_name = name_parts[0]
                    return f"Hallo {first_name},"
                else:
                    # Formal German: "Sehr geehrte/r Frau/Herr LastName"
                    # Try to detect gender from title, otherwise default to neutral
                    last_name = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
                    
                    # Simple heuristic: if name contains Frau/Ms./Mrs., use feminine
                    name_lower = contact_name.lower()
                    if any(title in name_lower for title in ['frau', 'ms.', 'mrs.']):
                        return f"Sehr geehrte Frau {last_name},"
                    elif any(title in name_lower for title in ['herr', 'mr.']):
                        return f"Sehr geehrter Herr {last_name},"
                    else:
                        # Gender-neutral or unknown: use full name
                        return f"Sehr geehrte/r {contact_name},"
            else:
                # English: always "Dear Name"
                return f"Dear {contact_name},"
        
        # No contact person: use generic team greeting
        if language == 'german':
            if formality == 'informal':
                # Informal: "Hallo" or "Liebes" for warmer tone
                if seniority in ['junior', 'mid']:
                    return f"Hallo {company_name}-Team,"
                else:
                    return f"Liebes {company_name}-Team,"
            else:
                # Formal: "Sehr geehrtes Team"
                return f"Sehr geehrtes {company_name}-Team,"
        else:
            # English: standard hiring team greeting
            if seniority in ['executive', 'senior']:
                return "Dear Hiring Manager,"
            else:
                return f"Dear {company_name} Hiring Team,"

    def generate_valediction(self, language: str, formality: str, seniority: str) -> str:
        """
        Generate appropriate valediction (closing) based on language and context.
        
        Args:
            language: 'german' or 'english'
            formality: 'formal' or 'informal'
            seniority: Seniority level for tone matching
            
        Returns:
            Appropriate valediction string
        """
        if language == 'german':
            if formality == 'informal':
                # Informal German closings
                if seniority in ['junior', 'mid']:
                    return "Viele Grüße"  # Very casual, friendly
                else:
                    return "Beste Grüße"  # Still casual but slightly more professional
            else:
                # Formal German: standard professional closing
                return "Mit freundlichen Grüßen"
        else:
            # English closings (with comma)
            if seniority in ['executive', 'senior']:
                return "Sincerely,"  # Most formal
            elif formality == 'informal':
                return "Best,"  # Modern, slightly casual
            else:
                return "Best regards,"  # Professional standard

    def generate_cover_letter(self, job_data: Dict[str, Any], target_language: Optional[str] = None, *, tone: Optional[str] = None, auto_trim: bool = False) -> str:
        job_description = job_data.get('job_description', '')
        if not target_language:
            target_language = self.detect_language(job_description)
        cv_text = self.cv_de if target_language == 'german' else self.cv_en
        if not cv_text:
            self.logger.error("CV not available for language: %s", target_language)
            raise AIGenerationError(f"CV not available for language: {target_language}")
        job_title = job_data.get('job_title', '')
        seniority = self.detect_seniority(job_title, job_description)
        
        # Detect formality for German language
        formality = 'formal'  # default
        if target_language == 'german':
            formality = self.detect_german_formality(job_description)
            self.logger.info("Detected German formality: %s", formality)
        
        # Generate salutation
        salutation = self.generate_salutation(job_data, target_language, formality, seniority)
        self.logger.debug("Generated salutation: %s", salutation)
        
        # Generate main body text (AI-generated)
        prompt = self._build_prompt(job_data, cv_text, target_language, seniority, tone=tone, formality=formality)
        if not self.client:
            self.logger.error("OpenAI client not available")
            raise AIGenerationError("OpenAI client not available")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(target_language, seniority)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
        except Exception as e:
            # Catch and wrap OpenAI client exceptions
            self.logger.error("OpenAI API error: %s", e)
            raise AIGenerationError(f"OpenAI API error: {e}") from e

        cover_letter_body = response.choices[0].message.content.strip()

        # Enforce 180–240 words (optionally nudge with auto_trim)
        word_count = len(re.findall(r"\b\w+\b", cover_letter_body))
        if (word_count < 180 or word_count > 240) and auto_trim:
            cover_letter_body = self._auto_trim_to_range(cover_letter_body, 180, 240)
            word_count = len(re.findall(r"\b\w+\b", cover_letter_body))
        if word_count < 180 or word_count > 240:
            self.logger.warning("Cover letter word count %s outside 180–240 range", word_count)
            raise AIGenerationError(f"Cover letter length out of bounds: {word_count} words")
        
        # Generate valediction
        valediction = self.generate_valediction(target_language, formality, seniority)
        self.logger.debug("Generated valediction: %s", valediction)
        
        # Store all three parts in job_data for docx_generator
        job_data['cover_letter_salutation'] = salutation
        job_data['cover_letter_body'] = cover_letter_body
        job_data['cover_letter_valediction'] = valediction
        
        self.logger.info("Generated complete cover letter: salutation=%s, body_words=%d, valediction=%s", 
                        salutation[:20] + "...", word_count, valediction)
        
        # Return body text for backward compatibility
        return cover_letter_body

    def _get_system_prompt(self, language: str, seniority: str) -> str:
        if language == 'german':
            return f"Du bist ein Experte für deutsche Bewerbungsanschreiben. Schreibe ein professionelles Anschreiben für eine {seniority}-Position."
        else:
            return f"You are an expert in writing professional English cover letters. Write a professional cover letter for a {seniority}-level position."

    def _build_prompt(self, job_data: Dict[str, Any], cv_text: str, language: str, seniority: str, *, tone: Optional[str] = None, formality: Optional[str] = None) -> str:
        company = job_data.get('company_name', 'the company')
        job_title = job_data.get('job_title', 'the position')
        job_desc = job_data.get('job_description', '')[:3000]
        location = job_data.get('location', '')
        cv_summary = cv_text[:2000] if cv_text else "No CV available"
        tone_line_de = f"Verwende einen {tone}-Ton." if tone and language == 'german' else ''
        tone_line_en = f"Use a {tone} tone." if tone and language != 'german' else ''
        
        # Add formality instruction for German
        formality_line_de = ''
        if language == 'german' and formality:
            if formality == 'informal':
                formality_line_de = "Verwende die Du-Form (informal)."
            else:
                formality_line_de = "Verwende die Sie-Form (formal)."
        
        if language == 'german':
            return f"""Schreibe ein Anschreiben für folgende Stelle:\n\nSTELLE:\nUnternehmen: {company}\nPosition: {job_title}\nOrt: {location}\n\nSTELLENBESCHREIBUNG:\n{job_desc}\n\nMEIN LEBENSLAUF (Auszug):\n{cv_summary}\n\nSchreibe ein überzeugendes Anschreiben, das:\n1. Einen persönlichen Bezug zur Firma/Mission herstellt\n2. 2-3 konkrete Beispiele aus meiner Erfahrung nutzt, die zur Stelle passen\n3. Meine relevanten Skills hervorhebt\n4. Zeigt, warum ich gut zur Stelle passe\n5. EXAKT 180-240 Wörter lang ist\n{tone_line_de}\n{formality_line_de}\n\nWICHTIG: Beginne den Text mit einem Kleinbuchstaben (z.B. 'mit großem Interesse...'), da nach der Grußformel im Deutschen der erste Buchstabe klein geschrieben wird.\n\nFormat: Nur der Fließtext des Anschreibens (ohne Anrede, ohne Adressblock, ohne Unterschrift am Ende)."""
        else:
            return f"""Write a cover letter for this position:\n\nJOB:\nCompany: {company}\nPosition: {job_title}\nLocation: {location}\n\nJOB DESCRIPTION:\n{job_desc}\n\nMY CV (Excerpt):\n{cv_summary}\n\nWrite a compelling cover letter that:\n1. Makes a personal connection to the company/mission\n2. Uses 2-3 concrete examples from my experience that match the role\n3. Highlights my relevant skills\n4. Shows why I am a great fit\n5. Is EXACTLY 180-240 words long\n{tone_line_en}\n\nFormat: Only the body text (no 'Dear Hiring Manager', no address block, no signature at the end)."""

    def _auto_trim_to_range(self, text: str, low: int, high: int) -> str:
        """Best-effort trimming/expansion to fit word range without changing meaning too much.

        Strategy: if too long, remove trailing sentences until within range; if too short, join lines and
        avoid aggressive expansion (we still keep strict check after this).
        """
        words = re.findall(r"\b\w+\b", text)
        if len(words) <= high and len(words) >= low:
            return text
        # Too long: remove last sentences
        if len(words) > high:
            sentences = re.split(r"(?<=[.!?])\s+", text.strip())
            while sentences and len(re.findall(r"\b\w+\b", " ".join(sentences))) > high:
                sentences = sentences[:-1]
            return " ".join(sentences).strip()
        # Too short: lightly compact whitespace (no expansion)
        compact = re.sub(r"\s+", " ", text).strip()
        return compact

    def save_cover_letter(self, cover_letter: str, job_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        if not filename:
            company = job_data.get('company_name', 'Company').replace(' ', '_')
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output/cover_letters/cover_letter_{company}_{timestamp}.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        self.logger.info("Cover letter saved: %s", filename)
        return filename
