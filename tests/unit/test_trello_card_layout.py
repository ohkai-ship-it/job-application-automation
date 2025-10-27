"""Tests for Trello card layout, labels, and custom fields."""
import pytest
from src.trello_connect import TrelloConnect


class FakeResponse:
    """Mock HTTP response."""
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
    
    def json(self):
        return self._json_data


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "company_name": "Tech Corp GmbH",
        "job_title": "Senior Python Developer (m/w/d)",
        "job_title_clean": "Senior Python Developer",
        "location": "Berlin",
        "work_mode": "hybrid",
        "language": "DE",
        "seniority": "senior",
        "source_url": "https://www.stepstone.de/job/123456",
        "stepstone_job_id": "123456",
        "company_job_reference": "REF-2025-001",
        "job_description": "We are looking for an experienced Python developer to join our team. You will work on exciting projects using Django, FastAPI, and modern cloud technologies. " * 3,
        "company_address_line1": "Tech Street 42",
        "company_address_line2": "10115 Berlin",
        "career_page_link": "https://techcorp.de/careers",
        "direct_apply_link": "https://techcorp.de/apply/123456",
    }


def test_build_card_name(sample_job_data):
    """Test card name formatting."""
    tc = TrelloConnect()
    name = tc._build_card_name(sample_job_data)
    
    assert name == "[Tech Corp GmbH] Senior Python Developer (Berlin)"


def test_build_card_description_contains_all_sections(sample_job_data):
    """Test that description returns only the job description text."""
    tc = TrelloConnect()
    desc = tc._build_card_description(sample_job_data)
    
    # Description should be only the job_description field (tripled in sample data)
    expected_desc = sample_job_data['job_description']
    assert desc == expected_desc
    assert "We are looking for an experienced Python developer" in desc


def test_build_card_description_handles_missing_fields():
    """Test that description handles missing job_description field gracefully."""
    minimal_data = {
        "company_name": "Acme Inc",
        "job_title": "Developer",
        "location": "Munich",
    }
    
    tc = TrelloConnect()
    desc = tc._build_card_description(minimal_data)
    
    # Should return default message when job_description is missing
    assert desc == "No job description available"


def test_get_label_ids_work_mode(sample_job_data, monkeypatch):
    """Test label mapping for work mode."""
    monkeypatch.setenv("TRELLO_LABEL_HYBRID", "label_hybrid_123")
    
    tc = TrelloConnect()
    labels = tc._get_label_ids(sample_job_data)
    
    assert "label_hybrid_123" in labels


def test_get_label_ids_language(sample_job_data, monkeypatch):
    """Test label mapping for language."""
    monkeypatch.setenv("TRELLO_LABEL_DE", "label_de_456")
    
    tc = TrelloConnect()
    labels = tc._get_label_ids(sample_job_data)
    
    assert "label_de_456" in labels


def test_get_label_ids_seniority(sample_job_data, monkeypatch):
    """Test label mapping for seniority."""
    monkeypatch.setenv("TRELLO_LABEL_SENIOR", "label_senior_789")
    
    tc = TrelloConnect()
    labels = tc._get_label_ids(sample_job_data)
    
    assert "label_senior_789" in labels


def test_get_label_ids_multiple_labels(sample_job_data, monkeypatch):
    """Test that multiple labels are collected."""
    monkeypatch.setenv("TRELLO_LABEL_HYBRID", "lbl1")
    monkeypatch.setenv("TRELLO_LABEL_DE", "lbl2")
    monkeypatch.setenv("TRELLO_LABEL_SENIOR", "lbl3")
    
    tc = TrelloConnect()
    labels = tc._get_label_ids(sample_job_data)
    
    assert len(labels) == 3
    assert "lbl1" in labels
    assert "lbl2" in labels
    assert "lbl3" in labels


def test_check_existing_card_by_name(sample_job_data, monkeypatch):
    """Test idempotency check by card name."""
    existing_cards = [
        {"id": "card123", "name": "[Tech Corp GmbH] Senior Python Developer (Berlin)", "desc": ""},
        {"id": "card456", "name": "Other Job", "desc": ""},
    ]
    
    def fake_requester(method, url, **kwargs):
        if "lists/" in url and "/cards" in url:
            return FakeResponse(200, existing_cards)
        return FakeResponse(404)
    
    monkeypatch.setenv("TRELLO_LIST_ID_LEADS", "list123")
    
    tc = TrelloConnect(requester=fake_requester)
    card_name = tc._build_card_name(sample_job_data)
    existing_id = tc._check_existing_card(card_name, sample_job_data["source_url"])
    
    assert existing_id == "card123"


def test_check_existing_card_by_source_url(sample_job_data, monkeypatch):
    """Test idempotency check by source URL in description."""
    existing_cards = [
        {"id": "card789", "name": "Different Name", "desc": "Source: https://www.stepstone.de/job/123456"},
    ]
    
    def fake_requester(method, url, **kwargs):
        if "lists/" in url and "/cards" in url:
            return FakeResponse(200, existing_cards)
        return FakeResponse(404)
    
    monkeypatch.setenv("TRELLO_LIST_ID_LEADS", "list123")
    
    tc = TrelloConnect(requester=fake_requester)
    card_name = tc._build_card_name(sample_job_data)
    existing_id = tc._check_existing_card(card_name, sample_job_data["source_url"])
    
    assert existing_id == "card789"


def test_create_card_with_labels_and_custom_fields(sample_job_data, monkeypatch, capsys):
    """Test full card creation with labels and custom fields."""
    created_card = {"id": "new_card_123", "shortUrl": "https://trello.com/c/new_card_123"}
    calls = []
    
    def fake_requester(method, url, **kwargs):
        calls.append({"method": method, "url": url, "kwargs": kwargs})
        
        # Check existing cards - return empty
        if method == "GET" and "lists/" in url:
            return FakeResponse(200, [])
        
        # Create card
        if method == "POST" and url.endswith("/cards"):
            return FakeResponse(201, created_card)
        
        # Set custom field
        if method == "PUT" and "/customField/" in url:
            return FakeResponse(200, {})
        
        return FakeResponse(404)
    
    # Configure env
    monkeypatch.setenv("TRELLO_KEY", "test_key")
    monkeypatch.setenv("TRELLO_TOKEN", "test_token")
    monkeypatch.setenv("TRELLO_LIST_ID_LEADS", "list123")
    monkeypatch.setenv("TRELLO_LABEL_HYBRID", "lbl_hybrid")
    monkeypatch.setenv("TRELLO_LABEL_DE", "lbl_de")
    monkeypatch.setenv("TRELLO_LABEL_SENIOR", "lbl_senior")
    # Set the actual field env vars the code expects
    monkeypatch.setenv("TRELLO_FIELD_FIRMENNAME", "field_company")
    monkeypatch.setenv("TRELLO_FIELD_ROLLENTITEL", "field_title")
    monkeypatch.setenv("TRELLO_FIELD_FIRMA_PERSON", "field_firma_person")
    
    tc = TrelloConnect(requester=fake_requester)
    result = tc.create_card_from_job_data(sample_job_data)
    
    assert result is not None
    assert result["id"] == "new_card_123"
    
    # Check that POST /cards was called with correct labels
    create_call = next(c for c in calls if c["method"] == "POST" and c["url"].endswith("/cards"))
    params = create_call["kwargs"]["params"]
    
    assert params["idList"] == "list123"
    assert params["name"] == "[Tech Corp GmbH] Senior Python Developer (Berlin)"
    assert "lbl_hybrid" in params["idLabels"]
    assert "lbl_de" in params["idLabels"]
    assert "lbl_senior" in params["idLabels"]
    
    # Check that custom fields were set
    field_calls = [c for c in calls if c["method"] == "PUT" and "/customField/" in c["url"]]
    assert len(field_calls) >= 2  # At least company and job title


def test_create_card_returns_existing_if_found(sample_job_data, monkeypatch, capsys):
    """Test that existing card is returned without creating duplicate."""
    existing_cards = [
        {"id": "existing123", "name": "[Tech Corp GmbH] Senior Python Developer (Berlin)", "desc": ""},
    ]
    
    calls = []
    
    def fake_requester(method, url, **kwargs):
        calls.append({"method": method, "url": url})
        
        if method == "GET" and "lists/" in url:
            return FakeResponse(200, existing_cards)
        
        return FakeResponse(404)
    
    monkeypatch.setenv("TRELLO_KEY", "test_key")
    monkeypatch.setenv("TRELLO_TOKEN", "test_token")
    monkeypatch.setenv("TRELLO_LIST_ID_LEADS", "list123")
    
    tc = TrelloConnect(requester=fake_requester)
    result = tc.create_card_from_job_data(sample_job_data)
    
    assert result is not None
    assert result["id"] == "existing123"
    assert result.get("already_exists") is True
    
    # Should not have made a POST request
    post_calls = [c for c in calls if c["method"] == "POST"]
    assert len(post_calls) == 0
