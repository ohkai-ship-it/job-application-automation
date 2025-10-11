"""
Unit tests for cover letter AI functionality
"""
import os
from unittest import mock
import pytest
from src.cover_letter import CoverLetterGenerator
from src.utils.env import load_env, validate_env
from openai import OpenAIError

@pytest.fixture(autouse=True)
def mock_env():
    """Fixture to provide mock environment for all tests"""
    with mock.patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'test-model'
    }, clear=True):
        load_env()
        yield

def test_cover_letter_generator_init_with_env():
    """Test CoverLetterGenerator initialization with environment variables"""
    generator = CoverLetterGenerator()
    assert generator.api_key == 'test-key'
    assert generator.model == 'test-model'

def test_cover_letter_generator_init_without_api_key():
    """Test CoverLetterGenerator fails without API key"""
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises((ValueError, OpenAIError)) as exc_info:
            CoverLetterGenerator()
        assert "OPENAI_API_KEY" in str(exc_info.value)

def test_cover_letter_generator_init_with_default_model():
    """Test CoverLetterGenerator uses default model if not in env"""
    with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}, clear=True):
        generator = CoverLetterGenerator()
        assert generator.api_key == 'test-key'
        assert generator.model == 'gpt-4o-mini'  # Default model

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