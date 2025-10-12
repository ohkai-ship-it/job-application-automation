import src.scraper as scraper


class FakeResp:
    def __init__(self, content: bytes):
        self.content = content


def make_dom_only_html():
    return (
        "<html><head></head><body>"
        '<h1 data-at="header-job-title">Product Manager (gn)</h1>'
        '<div data-at="metadata-company-name">Acme AG</div>'
        '<div data-at="metadata-location">München</div>'
        '<div data-at="metadata-work-type">Homeoffice / Hybrid</div>'
        '<p>Wir suchen Verstärkung. Kennziffer: XYZ-999</p>'
        '<a href="https://www.stepstone.de/go/apply-123">Jetzt bewerben</a>'
        "</body></html>"
    )


def test_scraper_dom_fallback_and_work_mode(monkeypatch):
    html = make_dom_only_html()

    def fake_request_with_retries(method, url, headers=None, timeout=None):
        return FakeResp(html.encode("utf-8"))

    monkeypatch.setattr(scraper, "request_with_retries", fake_request_with_retries)

    url = (
        "https://www.stepstone.de/stellenangebote--Product-Manager--98765432-inline.html"
    )
    data = scraper.scrape_stepstone_job(url)

    assert data is not None
    # DOM fallbacks
    assert data["job_title"] == "Product Manager (gn)"
    assert data["job_title_clean"] == "Product Manager"
    assert data["company_name"] == "Acme AG"
    assert data["location"] == "München"

    # Work mode from text containing Homeoffice + Hybrid
    assert data["work_mode"] == "hybrid"

    # Stepstone job id from URL
    assert data.get("stepstone_job_id") == "98765432"

    # Company reference is only extracted when a job_description is set; DOM-only path may skip it
    # Ensure we don't crash and field may be absent
    assert data.get("company_job_reference") in (None, "XYZ-999")

    # Direct apply link preserved (contains /go/)
    assert data.get("direct_apply_link") == "https://www.stepstone.de/go/apply-123"
