"""
Unit tests for Trello manager functionality
"""
import pytest
from src.trello_connect import TrelloConnect

def test_trello_connect_init():
    """Test TrelloConnect initialization"""
    manager = TrelloConnect()
    assert manager.api_key  # Should not be empty
    assert manager.board_id  # Should not be empty
    assert manager.leads_list_id  # Should not be empty

def test_trello_connect_custom_fields():
    """Test custom field IDs are initialized"""
    manager = TrelloConnect()
    assert 'company_name' in manager.custom_fields
    assert 'job_title' in manager.custom_fields
    assert 'source' in manager.custom_fields
    assert manager.stepstone_option_id == "67adec40a91936eec7f48587"

def test_trello_manager_labels():
    """Test label IDs are initialized"""
    manager = TrelloConnect()
    assert 'remote' in manager.labels
    assert 'hybrid' in manager.labels
    assert 'onsite' in manager.labels
    assert 'interesting' in manager.labels