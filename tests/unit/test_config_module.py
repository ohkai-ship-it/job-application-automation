import os
import json
import builtins
from pathlib import Path

import pytest

# The repo refers to utils.env as the config module; add focused tests for it
from src.utils import env as config


def test_load_env_reads_config_env():
    """Test that load_env reads environment-specific config files
    
    With the new environment-specific config system:
    - config/.env.{APP_ENV} takes precedence
    - config/.env serves as fallback
    
    This integration test verifies the system works end-to-end.
    """
    # Load the default environment configuration
    result = config.load_env()
    
    # Should successfully load config
    assert result == True
    
    # Verify some environment variables are loaded from .env
    # (These should be present in config/.env)
    assert os.getenv("TRELLO_KEY") is not None
    assert os.getenv("OPENAI_API_KEY") is not None


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
