"""
Unit tests for cover letter AI functionality
"""
import os
from unittest import mock
import pytest
from src.cover_letter import CoverLetterGenerator
from src.utils.env import load_env, validate_env
from openai import OpenAIError
from src.utils.errors import AIGenerationError

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


def test_generate_cover_letter_handles_openai_exception(monkeypatch):
    ai = CoverLetterGenerator()
    # Provide dummy CV text so the flow reaches the OpenAI call
    ai.cv_en = "dummy cv text " * 50
    ai.cv_de = "dummy cv text " * 50

    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    raise RuntimeError("quota exceeded")

    ai.client = DummyClient()

    with pytest.raises(AIGenerationError) as exc:
        ai.generate_cover_letter({
            'job_title': 'Engineer',
            'job_description': 'We do things',
            'company_name': 'Acme'
        }, target_language='english')
    # The error message comes from the exponential backoff decorator which wraps non-API exceptions
    assert 'Unexpected error' in str(exc.value) or 'quota exceeded' in str(exc.value)


def test_generate_cover_letter_word_count_enforced(monkeypatch):
    ai = CoverLetterGenerator()
    # Provide dummy CV text so the flow reaches the response validation
    ai.cv_en = "dummy cv text " * 50
    ai.cv_de = "dummy cv text " * 50

    class DummyResponse:
        def __init__(self, content: str):
            self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]

    import types

    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    # Return a too-short letter (<180 words)
                    return DummyResponse("too short")

    ai.client = DummyClient()

    with pytest.raises(AIGenerationError) as exc:
        ai.generate_cover_letter({
            'job_title': 'Engineer',
            'job_description': 'We do things',
            'company_name': 'Acme'
        }, target_language='english')
    assert 'length out of bounds' in str(exc.value)


def test_generate_cover_letter_raises_when_cv_missing():
    ai = CoverLetterGenerator()
    # Ensure no CV available for english
    ai.cv_en = None
    ai.cv_de = "dummy cv text"  # keep german available to ensure language branch selection matters

    with pytest.raises(AIGenerationError) as exc:
        ai.generate_cover_letter({
            'job_title': 'Engineer',
            'job_description': 'This description is in English and should select english language.',
            'company_name': 'Acme'
        }, target_language='english')
    assert 'CV not available' in str(exc.value)


def test_generate_cover_letter_raises_when_client_missing():
    ai = CoverLetterGenerator()
    # Provide CV so it reaches client check
    ai.cv_en = "dummy cv text " * 50
    ai.cv_de = "dummy cv text " * 50
    # Simulate missing client
    ai.client = None

    with pytest.raises(AIGenerationError) as exc:
        ai.generate_cover_letter({
            'job_title': 'Engineer',
            'job_description': 'We do things',
            'company_name': 'Acme'
        }, target_language='english')
    assert 'client not available' in str(exc.value)


def test_save_cover_letter_writes_file(tmp_path):
    ai = CoverLetterGenerator()
    text = "Hello world"
    out_file = tmp_path / 'out.txt'
    path = ai.save_cover_letter(text, {'company_name': 'Acme'}, filename=str(out_file))
    assert path == str(out_file)
    with open(path, 'r', encoding='utf-8') as f:
        assert f.read() == text


def test_get_system_prompt_language_variants():
    ai = CoverLetterGenerator()
    de_prompt = ai._get_system_prompt('german', 'senior')
    en_prompt = ai._get_system_prompt('english', 'junior')
    assert 'deutsche Bewerbungsanschreiben' in de_prompt
    assert 'English cover letters' in en_prompt