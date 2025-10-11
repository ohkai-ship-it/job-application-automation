import json
import pytest

from src.utils.html import parse_html, extract_json_ld_blocks, search_keywords


def test_extract_json_ld_blocks_handles_object_and_list():
    html = """
    <html><head>
      <script type="application/ld+json">{"@type": "JobPosting", "title": "Engineer"}</script>
      <script type="application/ld+json">[{"@type": "Organization", "name": "Acme"}, {"@type": "BreadcrumbList"}]</script>
      <script type="application/ld+json">not valid json</script>
    </head><body></body></html>
    """
    soup = parse_html(html)
    blocks = extract_json_ld_blocks(soup)
    # Should parse the object and each dict within the list; skip invalid
    assert any(b.get("@type") == "JobPosting" for b in blocks)
    assert any(b.get("@type") == "Organization" for b in blocks)
    # Non-dict entries should be ignored
    assert all(isinstance(b, dict) for b in blocks)


def test_search_keywords_returns_context_objects():
    html = """
    <html><body>
      <div class="meta">Berlin Office</div>
      <p>Company: Aignostics GmbH</p>
      <section><span>Ihre Aufgaben: Entwicklung</span></section>
    </body></html>
    """
    soup = parse_html(html)
    keywords = {"company": "Aignostics", "location": "Berlin", "desc": "Ihre Aufgaben"}
    results = search_keywords(soup, keywords, limit_per=2)

    assert set(results.keys()) == set(keywords.keys())
    # Ensure each hit includes the expected shape
    for key, occs in results.items():
        for occ in occs:
            assert "parent_tag" in occ
            assert "classes" in occ
            assert "preview" in occ
            assert isinstance(occ["classes"], list)
