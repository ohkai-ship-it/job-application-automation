"""
Unit tests for Trello manager functionality
"""
import pytest
from src.trello_connect import TrelloConnect

def test_trello_connect_init():
    """Test TrelloConnect initialization"""
    manager = TrelloConnect()
    assert manager.api_key == "your-trello-key"
    assert manager.board_id == "your-board-id"
    assert manager.leads_list_id == "67ade7af134e9f72c55b4dd9"

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