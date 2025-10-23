import os
from pathlib import Path
from unittest import mock

import pytest

# Skip hard env validation under test
os.environ.setdefault("SKIP_ENV_VALIDATION", "1")

from src import main


@pytest.fixture(autouse=True)
def patch_env(monkeypatch, tmp_path):
    # Minimal required env for paths
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "out"))
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "out" / "cover_letters").mkdir(parents=True, exist_ok=True)

    # OpenAI unavailable to avoid network
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")


def fake_scrape(url: str):
    return {
        "company_name": "TestCo",
        "job_title": "Engineer (m/w/d)",
        "job_description": "We build things and collaborate.",
        "location": "Berlin",
        "source_url": url,
    }


def test_process_job_posting_happy_path(monkeypatch, tmp_path):
    # Patch scraper
    monkeypatch.setattr(main, "scrape_job_posting", lambda url: fake_scrape(url))
    # Patch Trello client to avoid network
    class FakeTrello:
        def create_card_from_job_data(self, job_data):
            return {"shortUrl": "https://trello.example/card"}
    monkeypatch.setattr(main, "TrelloConnect", lambda: FakeTrello())

    # Patch cover letter generator to avoid OpenAI
    class FakeAI:
        def detect_language(self, *_):
            return "english"
        def detect_seniority(self, *_, **__):
            return "mid"
        def generate_cover_letter(self, *_, **__):  # Accept target_language kwarg
            return "Short body text for testing."
        def generate_salutation(self, job_data, language, formality, seniority):
            return "Dear Hiring Manager,"
        def generate_valediction(self, language, formality, seniority):
            return "Sincerely,\nKai Voges"
        def save_cover_letter(self, cover_letter, job_data, filename=None):
            p = tmp_path / "out" / "cover_letters" / "letter.txt"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(cover_letter, encoding="utf-8")
            return str(p)
    monkeypatch.setattr(main, "CoverLetterGenerator", lambda: FakeAI())

    # Patch Word generator to avoid DOCX/PDF complexity
    class FakeWord:
        sender = {'name': 'Dr. Kai Voges'}
        
        def generate_from_template(self, text, job, docx_filename, language="english"):
            p = tmp_path / "out" / "cover_letters" / "letter.docx"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("docx", encoding="utf-8")
            return str(p)
        def convert_to_pdf(self, docx_file, pdf_filename):
            p = tmp_path / "out" / "cover_letters" / "letter.pdf"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("pdf", encoding="utf-8")
            return str(p)
    monkeypatch.setattr(main, "WordCoverLetterGenerator", lambda: FakeWord())

    url = "https://www.stepstone.de/stellenangebote--Example--123-inline.html"
    result = main.process_job_posting(url, generate_cover_letter=True, generate_pdf=False)

    assert result["status"] == "success"
    assert result["job_data"]["company_name"] == "TestCo"
    assert result["trello_card"]["shortUrl"].startswith("https://trello.example/")
    # data_file is disabled, so we don't check it
    # TXT file generation is skipped (not needed), so we don't check it
    assert Path(result["cover_letter_docx_file"]).exists()
    # PDF generation is disabled by default
    # assert Path(result["cover_letter_pdf_file"]).exists()
