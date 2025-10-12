import types
from typing import Any

import requests

from src import scraper as scraper_mod


class DummyResponse:
    def __init__(self, content: bytes, status_code: int = 200, text: str = ""):
        self.content = content
        self.status_code = status_code
        self.text = text or content.decode("utf-8", errors="ignore")


def test_scrape_stepstone_job_http_404(monkeypatch):
    def fake_request_with_retries(method: str, url: str, **kwargs: Any):
        err = requests.HTTPError("Not Found")
        err.response = types.SimpleNamespace(status_code=404, text="not found")
        raise err

    monkeypatch.setattr(scraper_mod, "request_with_retries", fake_request_with_retries)

    result = scraper_mod.scrape_stepstone_job("https://example.com/job/404")
    assert result is None


def test_scrape_stepstone_job_network_error(monkeypatch):
    def fake_request_with_retries(method: str, url: str, **kwargs: Any):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(scraper_mod, "request_with_retries", fake_request_with_retries)

    result = scraper_mod.scrape_stepstone_job("https://example.com/job/neterr")
    assert result is None


def test_scrape_stepstone_job_malformed_html(monkeypatch):
    bad_html = b"<html><head><script type='application/ld+json'>{invalid json}</script></head><body><div></div></body></html>"

    def fake_request_with_retries(method: str, url: str, **kwargs: Any):
        return DummyResponse(content=bad_html)

    monkeypatch.setattr(scraper_mod, "request_with_retries", fake_request_with_retries)

    url = "https://example.com/job/malformed"
    result = scraper_mod.scrape_stepstone_job(url)
    assert isinstance(result, dict)
    # Minimal safe payload returned
    assert result["source_url"] == url
    # With malformed HTML/JSON-LD, most fields will be None
    assert result.get("job_title") is None
    assert result.get("company_name") is None