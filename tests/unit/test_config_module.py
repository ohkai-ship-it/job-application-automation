import os
import json
import builtins
from pathlib import Path

import pytest

# The repo refers to utils.env as the config module; add focused tests for it
from src.utils import env as config


def test_load_env_reads_config_env(tmp_path, monkeypatch):
    # Create a temporary .env file under config/
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    env_path = cfg_dir / ".env"
    env_path.write_text("TRELLO_KEY=abc\nTRELLO_TOKEN=xyz\nFLASK_PORT=5050\n", "utf-8")

    # Point the module's ENV_PATH to our temp file to avoid reading real repo .env
    monkeypatch.setattr(config, "ENV_PATH", env_path)

    # Ensure process env is clean for these vars
    for k in ["TRELLO_KEY", "TRELLO_TOKEN", "FLASK_PORT"]:
        monkeypatch.delenv(k, raising=False)

    config.load_env()  # should pick up our patched ENV_PATH

    assert os.getenv("TRELLO_KEY") == "abc"
    assert os.getenv("TRELLO_TOKEN") == "xyz"
    assert os.getenv("FLASK_PORT") == "5050"


def test_get_str_and_default(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    assert config.get_str("FOO", default="x") == "bar"
    assert config.get_str("MISSING", default="x") == "x"


def test_validate_env_success(monkeypatch):
    # Provide required variables
    monkeypatch.setenv("TRELLO_KEY", "k")
    monkeypatch.setenv("TRELLO_TOKEN", "t")
    monkeypatch.setenv("FLASK_HOST", "127.0.0.1")
    monkeypatch.setenv("FLASK_PORT", "5000")

    config.validate_env(["TRELLO_KEY", "TRELLO_TOKEN", "FLASK_HOST", "FLASK_PORT"])


def test_validate_env_invalid_port(monkeypatch):
    # validate_env only checks presence; invalid port is validated in validate_all_env
    env_vars = {
        'OPENAI_API_KEY': 'x',
        'TRELLO_KEY': 'k',
        'TRELLO_TOKEN': 't',
        'TRELLO_BOARD_ID': 'b',
        'TRELLO_LIST_ID_LEADS': 'l',
        'FLASK_HOST': '127.0.0.1',
        'FLASK_PORT': '-1',
        'DATA_DIR': 'data',
        'OUTPUT_DIR': 'output',
    }
    for k, v in env_vars.items():
        monkeypatch.setenv(k, v)
    # Avoid reading actual .env
    monkeypatch.setattr(config, "load_env", lambda: True)
    with pytest.raises(ValueError):
        config.validate_all_env()


def test_validate_all_env_missing(monkeypatch):
    # Clear envs
    for k in [
        'OPENAI_API_KEY','TRELLO_KEY','TRELLO_TOKEN','TRELLO_BOARD_ID','TRELLO_LIST_ID_LEADS',
        'FLASK_HOST','FLASK_PORT','DATA_DIR','OUTPUT_DIR']:
        monkeypatch.delenv(k, raising=False)
    # Avoid reading actual .env file
    monkeypatch.setattr(config, "load_env", lambda: True)
    with pytest.raises(ValueError):
        config.validate_all_env()
