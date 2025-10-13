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
    from .utils.logging import get_logger
    from .utils.errors import AIGenerationError
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.env import get_str
    from utils.logging import get_logger
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
        prompt = self._build_prompt(job_data, cv_text, target_language, seniority, tone=tone)
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

        cover_letter = response.choices[0].message.content.strip()

        # Enforce 180–240 words (optionally nudge with auto_trim)
        word_count = len(re.findall(r"\b\w+\b", cover_letter))
        if (word_count < 180 or word_count > 240) and auto_trim:
            cover_letter = self._auto_trim_to_range(cover_letter, 180, 240)
            word_count = len(re.findall(r"\b\w+\b", cover_letter))
        if word_count < 180 or word_count > 240:
            self.logger.warning("Cover letter word count %s outside 180–240 range", word_count)
            raise AIGenerationError(f"Cover letter length out of bounds: {word_count} words")
        return cover_letter

    def _get_system_prompt(self, language: str, seniority: str) -> str:
        if language == 'german':
            return f"Du bist ein Experte für deutsche Bewerbungsanschreiben. Schreibe ein professionelles Anschreiben für eine {seniority}-Position."
        else:
            return f"You are an expert in writing professional English cover letters. Write a professional cover letter for a {seniority}-level position."

    def _build_prompt(self, job_data: Dict[str, Any], cv_text: str, language: str, seniority: str, *, tone: Optional[str] = None) -> str:
        company = job_data.get('company_name', 'the company')
        job_title = job_data.get('job_title', 'the position')
        job_desc = job_data.get('job_description', '')[:3000]
        location = job_data.get('location', '')
        cv_summary = cv_text[:2000] if cv_text else "No CV available"
        tone_line_de = f"Verwende einen {tone}-Ton." if tone and language == 'german' else ''
        tone_line_en = f"Use a {tone} tone." if tone and language != 'german' else ''
        if language == 'german':
            return f"""Schreibe ein Anschreiben für folgende Stelle:\n\nSTELLE:\nUnternehmen: {company}\nPosition: {job_title}\nOrt: {location}\n\nSTELLENBESCHREIBUNG:\n{job_desc}\n\nMEIN LEBENSLAUF (Auszug):\n{cv_summary}\n\nSchreibe ein überzeugendes Anschreiben, das:\n1. Einen persönlichen Bezug zur Firma/Mission herstellt\n2. 2-3 konkrete Beispiele aus meiner Erfahrung nutzt, die zur Stelle passen\n3. Meine relevanten Skills hervorhebt\n4. Zeigt, warum ich gut zur Stelle passe\n5. EXAKT 180-240 Wörter lang ist\n{tone_line_de}\n\nFormat: Nur der Fließtext des Anschreibens (ohne Anrede, ohne Adressblock, ohne Unterschrift am Ende)."""
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
