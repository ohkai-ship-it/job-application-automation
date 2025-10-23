import json
from pathlib import Path

import pytest

from src.main import process_job_posting


@pytest.mark.parametrize(
    "url",
    [
        # Use an obviously invalid URL to force scraper failure path without network
        "http://invalid.localhost.invalid/",
    ],
)
def test_error_file_created_on_scrape_failure(tmp_path, monkeypatch, url):
    # Redirect OUTPUT_DIR and DATA_DIR so test has no side effects
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SKIP_ENV_VALIDATION", "1")

    # Monkeypatch scraper to return None to simulate failure fast
    import src
    from src import main as main_module

    def fake_scrape(_url):
        return None

    # Patch in place where used
    monkeypatch.setattr(main_module, "scrape_stepstone_job", fake_scrape)

    result = process_job_posting(url, generate_cover_letter=False, generate_pdf=False)
    assert result["status"] == "failed"

    errors_dir = Path(tmp_path / "output" / "errors")
    files = list(errors_dir.glob("error_*.json"))
    assert files, "Expected an error report JSON to be created"

