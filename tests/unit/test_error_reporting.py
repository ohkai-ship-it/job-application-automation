import json
import os
from pathlib import Path

import pytest

from src.utils.error_reporting import report_error


def test_reporter_writes_file_and_masks_secrets(tmp_path, monkeypatch):
    # Redirect OUTPUT_DIR to tmp
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    context = {
        "token": "abcd1234",
        "nested": {"api_key": "supersecret"},
        "note": "x" * 3000,  # long string should be truncated
    }

    path = report_error("Something failed", context=context)
    assert path.exists()
    data = json.loads(path.read_text("utf-8"))

    # Shape
    assert data["message"] == "Something failed"
    assert data["severity"] == "error"
    assert "timestamp" in data and "id" in data

    # Sanitization
    assert data["context"]["token"] == "***"
    assert data["context"]["nested"]["api_key"] == "***"
    assert data["context"]["note"].endswith("…")
    assert len(data["context"]["note"]) <= 2001  # truncated with ellipsis


def test_reporter_includes_stack_on_exception(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    try:
        raise ValueError("boom")
    except Exception as e:
        path = report_error("Explosion", exc=e, context={"k": "v"})

    data = json.loads(path.read_text("utf-8"))
    assert data["exception_type"] == "ValueError"
    assert "ValueError: boom" in (data["stack"] or "")

