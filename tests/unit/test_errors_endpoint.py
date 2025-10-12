import json
from pathlib import Path

import pytest

from src.app import app


def test_errors_endpoint_lists_files(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    # App reads OUTPUT_DIR at import time; need to reconfigure app paths for this test
    from importlib import reload
    import src.app as app_module
    reload(app_module)

    client = app_module.app.test_client()

    # Ensure errors dir and drop a couple of files
    errors_dir = Path(tmp_path / "output" / "errors")
    errors_dir.mkdir(parents=True, exist_ok=True)
    (errors_dir / "error_20250101T000000Z.json").write_text(json.dumps({
        "id": "evt_1", "timestamp": "20250101T000000Z", "severity": "error", "message": "One"
    }), "utf-8")
    (errors_dir / "error_20250101T000100Z.json").write_text(json.dumps({
        "id": "evt_2", "timestamp": "20250101T000100Z", "severity": "warning", "message": "Two"
    }), "utf-8")

    resp = client.get("/errors?limit=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "errors" in data
    assert len(data["errors"]) == 1
    assert data["errors"][0]["id"] == "evt_2"  # newest first

