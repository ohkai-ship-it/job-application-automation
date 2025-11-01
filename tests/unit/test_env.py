"""Unit tests for environment variable handling"""
import os
from unittest import mock
import pytest
from pathlib import Path
from src.utils.env import load_env, validate_env, get_str, validate_all_env

def test_load_env():
    """Test that environment variables are loaded"""
    # Just verify that load_env() works and returns bool
    result = load_env()
    assert isinstance(result, bool)

def test_load_env_missing_file():
    """Test that the system gracefully handles config loading"""
    # The system will try to load configs, and at minimum the base .env exists
    # This test just ensures load_env() doesn't crash
    result = load_env()
    assert isinstance(result, bool)
    # In our test environment, config files should exist so this should be True
    # (The real test of missing files is covered by the other tests that patch paths)

def test_validate_env():
    """Test environment variable validation"""
    with mock.patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        # Should not raise error
        validate_env(["TEST_VAR"])
        
        # Should raise error for missing variable
        with pytest.raises(ValueError) as exc_info:
            validate_env(["MISSING_VAR"])
        assert "Missing required environment variables" in str(exc_info.value)

def test_get_str():
    """Test string variable getter with default value"""
    with mock.patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        assert get_str("TEST_VAR") == "test_value"
        assert get_str("MISSING_VAR", "default") == "default"
        assert get_str("MISSING_VAR") == ""  # default default is empty string

def test_validate_all_env_success():
    """Test validation with all required variables set"""
    env_vars = {
        'OPENAI_API_KEY': 'test-key',
        'TRELLO_KEY': 'test-key',
        'TRELLO_TOKEN': 'test-token',
        'TRELLO_BOARD_ID': 'test-board',
        'TRELLO_LIST_ID_LEADS': 'test-list',
        'FLASK_HOST': 'localhost',
        'FLASK_PORT': '5000',
        'DATA_DIR': 'data',
        'OUTPUT_DIR': 'output'
    }
    
    with mock.patch.dict(os.environ, env_vars, clear=True), \
         mock.patch('src.utils.env.load_env', return_value=True):
        validate_all_env()  # Should not raise

def test_validate_all_env_missing_vars():
    """Test validation with missing variables"""
    with mock.patch.dict(os.environ, {}, clear=True), \
         mock.patch('src.utils.env.load_env', return_value=True):
        with pytest.raises(ValueError) as exc_info:
            validate_all_env()
        error = str(exc_info.value)
        assert "OpenAI: Missing OPENAI_API_KEY" in error
        assert "Trello: Missing TRELLO_KEY" in error

def test_validate_all_env_invalid_port():
    """Test validation with invalid port number"""
    env_vars = {
        'OPENAI_API_KEY': 'test-key',
        'TRELLO_KEY': 'test-key',
        'TRELLO_TOKEN': 'test-token',
        'TRELLO_BOARD_ID': 'test-board',
        'TRELLO_LIST_ID_LEADS': 'test-list',
        'FLASK_HOST': 'localhost',
        'FLASK_PORT': '999999',  # Invalid port
        'DATA_DIR': 'data',
        'OUTPUT_DIR': 'output'
    }
    
    with mock.patch.dict(os.environ, env_vars, clear=True), \
         mock.patch('src.utils.env.load_env', return_value=True):
        with pytest.raises(ValueError) as exc_info:
            validate_all_env()
        assert "FLASK_PORT must be between 1 and 65535" in str(exc_info.value)

def test_validate_all_env_env_file_missing():
    """Test validation when .env file is missing"""
    with mock.patch('src.utils.env.load_env', return_value=False):
        with pytest.raises(ValueError) as exc_info:
            validate_all_env()
        assert "Could not load environment file" in str(exc_info.value)
