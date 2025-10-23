import json
from pathlib import Path

import pytest

import src.scraper as scraper


class FakeResp:
    def __init__(self, content: bytes):
        self.content = content


def make_html_with_jsonld() -> str:
    json_ld = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": "Senior Data Scientist (m/w/d)",
        "hiringOrganization": {
            "@type": "Organization",
            "name": "Aignostics GmbH",
            "url": "https://www.aignostics.com"
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Example Str. 1",
                "postalCode": "10115",
                "addressLocality": "Berlin",
                "addressCountry": "DE"
            }
        },
        "datePosted": "2025-10-12",
        "description": "<p>We are hiring! Referenznummer: ABC-123</p>",
        "identifier": {"@type": "PropertyValue", "value": "ABC-123"}
    }
    return f"""
    <html>
      <head>
        <script type="application/ld+json">{json.dumps(json_ld)}</script>
      </head>
      <body>
        <a href="https://apply.example.com" >Jetzt bewerben</a>
      </body>
    </html>
    """


def test_scraper_parses_jsonld_happy_path(monkeypatch):
    html = make_html_with_jsonld()

    def fake_request_with_retries(method, url, headers=None, timeout=None):
        return FakeResp(html.encode("utf-8"))

    monkeypatch.setattr(scraper, "request_with_retries", fake_request_with_retries)

    url = "https://www.stepstone.de/stellenangebote--Senior-Data-Scientist--12345678-inline.html"
    data = scraper.scrape_stepstone_job(url)

    assert data is not None
    assert data["job_title"] == "Senior Data Scientist (m/w/d)"
    assert data["job_title_clean"] == "Senior Data Scientist"
    assert data["company_name"] == "Aignostics GmbH"
    assert data["location"] == "Berlin"
    assert data["publication_date"] == "2025-10-12"
    assert "We are hiring!" in (data.get("job_description") or "")

    # Address lines
    assert data["company_address_line1"] == "Example Str. 1"
    assert data["company_address_line2"] == "10115 Berlin"

    # Website and career page
    assert data["website_link"] == "https://www.aignostics.com"
    assert data["career_page_link"].endswith("/karriere")

    # Direct apply link detected
    assert data["direct_apply_link"] == "https://apply.example.com"

    # Company reference number
    assert data["company_job_reference"] == "ABC-123"
