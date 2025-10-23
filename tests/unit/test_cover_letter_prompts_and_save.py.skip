import re
from pathlib import Path

import pytest

import src.cover_letter as cl


def test_build_prompt_contains_core_fields(monkeypatch):
    gen = cl.CoverLetterGenerator()
    gen.cv_en = "CV text"  # ensure not None for any indirect use
    job_data = {
        "company_name": "ACME",
        "job_title": "Engineer",
        "job_description": "We do things.",
        "location": "Berlin",
    }
    prompt = gen._build_prompt(job_data, "CV TEXT", "english", "senior")
    assert "ACME" in prompt and "Engineer" in prompt and "Berlin" in prompt
    assert "CV TEXT" in prompt


def test_save_cover_letter_default_path(monkeypatch, tmp_path):
    gen = cl.CoverLetterGenerator()
    # Redirect output dir
    monkeypatch.chdir(tmp_path)
    path = gen.save_cover_letter("hello", {"company_name": "Foo Bar GmbH"})
    assert Path(path).exists()
    assert Path(path).suffix == ".txt"
    assert "cover_letter_Foo_Bar_GmbH_" in Path(path).name
