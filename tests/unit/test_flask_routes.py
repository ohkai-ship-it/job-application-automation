import os
import json
import io
from unittest import mock

import pytest

# Ensure test-friendly import
os.environ.setdefault("SKIP_ENV_VALIDATION", "1")

from src.app import app, processing_status


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_index_route(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower() or b"<!doctype html" in resp.data.lower()


def test_process_and_status_flow(client, monkeypatch):
    # Fake background worker to immediately mark complete
    def fake_worker(job_id, url):
        processing_status[job_id] = {
            "status": "complete",
            "message": "done",
            "progress": 100,
            "result": {
                "company": "TestCo",
                "title": "Engineer",
                "location": "Berlin",
                "trello_card": "https://trello.example/abc",
                "files": {"json": "data/scraped_job_X.json"},
            },
        }

    monkeypatch.setattr("src.app.process_in_background", fake_worker)

    # POST with at least one processing option (create_trello_card=True)
    resp = client.post("/process", json={
        "url": "https://example.com/job",
        "create_trello_card": True,
        "generate_documents": False,
        "generate_pdf": False
    })
    assert resp.status_code == 200
    job_id = resp.get_json()["job_id"]

    # Now status should be complete
    s = client.get(f"/status/{job_id}")
    assert s.status_code == 200
    j = s.get_json()
    assert j["status"] in {"processing", "complete"}


def test_download_invalid_file_returns_404(client):
    resp = client.get("/download/does_not_exist.txt")
    assert resp.status_code == 404
