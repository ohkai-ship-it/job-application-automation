import requests
import pytest

from src.utils.http import request_with_retries


class DummyResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text or f"status={status_code}"

    def raise_for_status(self):
        raise requests.HTTPError(self.text, response=self)


def test_request_with_retries_success_after_transient(monkeypatch):
    calls = {"count": 0}
    sleeps: list[float] = []

    def fake_request(method, url, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return DummyResponse(429, text="rate limited")
        return DummyResponse(200, text="ok")

    def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr("time.sleep", fake_sleep)

    resp = request_with_retries("GET", "http://example.com/test")
    assert isinstance(resp, DummyResponse)
    assert resp.status_code == 200
    assert calls["count"] == 2
    # first backoff should be 0.5 by default
    assert sleeps == [0.5]


def test_request_with_retries_non_retryable_raises(monkeypatch):
    calls = {"count": 0}

    def fake_request(method, url, **kwargs):
        calls["count"] += 1
        return DummyResponse(401, text="unauthorized")

    monkeypatch.setattr(requests, "request", fake_request)

    with pytest.raises(requests.HTTPError):
        request_with_retries("POST", "http://example.com/resource")
    assert calls["count"] == 1


def test_request_with_retries_exhausts_and_raises(monkeypatch):
    calls = {"count": 0}
    sleeps: list[float] = []

    def fake_request(method, url, **kwargs):
        calls["count"] += 1
        return DummyResponse(503, text="service unavailable")

    def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr("time.sleep", fake_sleep)

    with pytest.raises(requests.HTTPError):
        request_with_retries("GET", "http://example.com/down", retries=2)

    # Should attempt retries+1 times: 3
    assert calls["count"] == 3
    # Should have slept exactly 'retries' times with exponential backoff: 0.5, 1.0
    assert sleeps == [0.5, 1.0]


def test_request_with_retries_exception_then_success(monkeypatch):
    calls = {"count": 0}
    sleeps: list[float] = []

    def fake_request(method, url, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.Timeout("timeout")
        return DummyResponse(200, text="ok")

    def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr("time.sleep", fake_sleep)

    resp = request_with_retries("GET", "http://example.com/slow")
    assert isinstance(resp, DummyResponse)
    assert resp.status_code == 200
    assert calls["count"] == 2
    assert sleeps == [0.5]
