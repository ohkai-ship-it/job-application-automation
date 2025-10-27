import re
from pathlib import Path
from unittest import mock
from io import BytesIO

import pytest

import src.cover_letter as cl


class DummyChoices:
    def __init__(self, content):
        class Msg:
            def __init__(self, c):
                self.content = c
        self.message = Msg(content)


class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoices(content)]


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, temperature, max_tokens):
                # Return a 200-word text
                words = ["word"] * 200
                return DummyResponse(" ".join(words))


class FakePage:
    def extract_text(self):
        return "Experience in data science and machine learning with Python."

class FakeReader:
    def __init__(self, file):
        self.pages = [FakePage(), FakePage()]


def test_generate_cover_letter_happy_path(monkeypatch):
    # Setup environment BEFORE creating the generator
    monkeypatch.setenv("OPENAI_API_KEY", "testkey")
    monkeypatch.setenv("OPENAI_MODEL", "dummy-model")

    # Mock os.path.exists to return True for CV files
    def fake_exists(path):
        return str(path).endswith("cv_de.pdf") or str(path).endswith("cv_en.pdf")
    monkeypatch.setattr(cl.os.path, "exists", fake_exists)

    # Mock open() to return a fake file object for CV files
    original_open = open
    def fake_open(filepath, *args, **kwargs):
        if str(filepath).endswith(('.pdf', 'cv_de.pdf', 'cv_en.pdf')):
            # Return a BytesIO object that looks like a PDF file
            return BytesIO(b'%PDF-1.4 fake pdf content')
        return original_open(filepath, *args, **kwargs)
    
    monkeypatch.setattr("builtins.open", fake_open)

    # Patch pypdf before generator init
    monkeypatch.setattr(cl, "pypdf", type("P", (), {"PdfReader": FakeReader}))

    # Now create generator - it will use the mocked pypdf, os.path.exists, and open
    gen = cl.CoverLetterGenerator()
    # Inject dummy client
    gen.client = DummyClient()

    job_data = {
        "company_name": "Aignostics GmbH",
        "job_title": "Senior Data Scientist",
        "job_description": "We need someone and the team and the mission",  # contains English markers
        "location": "Berlin",
    }

    result = gen.generate_cover_letter(job_data)

    # 200 words output
    assert len(re.findall(r"\b\w+\b", result)) == 200

