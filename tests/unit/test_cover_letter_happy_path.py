import re
from pathlib import Path

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


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    # Provide required env and dummy CV files
    monkeypatch.setenv("OPENAI_API_KEY", "testkey")
    monkeypatch.setenv("OPENAI_MODEL", "dummy-model")

    # Create dummy CVs with some text content
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Monkeypatch os.path.exists to return True for our dummy files
    # and pypdf reading to simulate content
    def fake_exists(path):
        return str(path).endswith("cv_de.pdf") or str(path).endswith("cv_en.pdf")

    monkeypatch.setattr(cl.os.path, "exists", fake_exists)

    class FakePage:
        def extract_text(self):
            return "Experience in data science."

    class FakeReader:
        def __init__(self, file):
            self.pages = [FakePage(), FakePage()]

    # Patch pypdf
    cl.pypdf = type("P", (), {"PdfReader": FakeReader})


def test_generate_cover_letter_happy_path(monkeypatch):
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

