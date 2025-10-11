"""
Unit tests for cover letter AI functionality
"""
import pytest
from src.cover_letter_ai import CoverLetterGenerator

def test_detect_language():
    """Test language detection functionality"""
    ai = CoverLetterGenerator()
    
    # German text
    german_text = """
    Wir suchen einen erfahrenen Entwickler für unser Team.
    Sie werden mit modernsten Technologien arbeiten.
    """
    assert ai.detect_language(german_text) == 'german'
    
    # English text
    english_text = """
    We are looking for an experienced developer.
    You will work with cutting-edge technologies.
    """
    assert ai.detect_language(english_text) == 'english'

def test_detect_seniority():
    """Test job seniority detection"""
    ai = CoverLetterGenerator()
    
    test_cases = [
        # Title, Description, Expected
        (
            "Junior Developer",
            "Entry level position for graduates",
            "junior"
        ),
        (
            "Senior Software Engineer",
            "Looking for experienced developers",
            "senior"
        ),
        (
            "Head of Engineering",
            "Lead our technical department",
            "executive"
        ),
        (
            "Software Developer",
            "Regular developer position",
            "mid"
        ),
    ]
    
    for title, desc, expected in test_cases:
        assert ai.detect_seniority(title, desc) == expected