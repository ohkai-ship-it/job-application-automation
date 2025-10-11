import json
from typing import Any, Dict
import types

import pytest

from src.trello_connect import TrelloConnect


class DummyResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any] | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text or json.dumps(self._payload)

    def json(self) -> Dict[str, Any]:
        return self._payload


def sample_job_data() -> Dict[str, Any]:
    return {
        'company_name': 'Acme Inc.',
        'job_title': 'Senior Engineer',
        'job_description': 'We are looking for...',
        'location': 'Remote',
        'source_url': 'https://example.com/job/123'
    }


def test_create_card_from_job_data_success(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, Any] = {}

    def fake_post(url: str, params: Dict[str, Any]):  # type: ignore[override]
        calls['url'] = url
        calls['params'] = params
        # Simulate Trello success payload
        return DummyResponse(200, payload={'id': 'card123', 'shortUrl': 'https://trello.com/c/abc123'})

    # Patch requests.post
    import requests  # local import so monkeypatch works in test environment
    monkeypatch.setattr(requests, 'post', fake_post)

    # Execute
    tc = TrelloConnect()
    result = tc.create_card_from_job_data(sample_job_data())

    # Assert
    assert result is not None
    assert calls['url'].endswith('/cards')
    assert calls['params']['idList'] == tc.leads_list_id
    assert calls['params']['name'] == 'Acme Inc. - Senior Engineer'
    assert 'desc' in calls['params'] and isinstance(calls['params']['desc'], str)
    assert calls['params']['pos'] == 'top'
    # Auth params included
    assert calls['params']['key'] == tc.api_key
    assert calls['params']['token'] == tc.token


def test_create_card_from_job_data_failure(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
    def fake_post(url: str, params: Dict[str, Any]):  # type: ignore[override]
        return DummyResponse(401, text='unauthorized')

    import requests
    monkeypatch.setattr(requests, 'post', fake_post)

    tc = TrelloConnect()
    result = tc.create_card_from_job_data(sample_job_data())

    # Should return None on failure
    assert result is None

    # Our implementation prints an error line; capture to make sure we at least emit something helpful
    out, err = capsys.readouterr()
    assert 'Trello API error' in out
