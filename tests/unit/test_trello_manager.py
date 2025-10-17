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
    # New implementation uses individual attributes instead of dict
    # Updated to match new field names from previous implementation
    assert hasattr(manager, 'field_company')
    assert hasattr(manager, 'field_job_title')
    assert hasattr(manager, 'field_source_url')  # Changed from field_source
    assert hasattr(manager, 'field_firma_person')
    assert hasattr(manager, 'field_source_list')
    assert hasattr(manager, 'field_publication_date')

def test_trello_manager_labels():
    """Test label IDs are initialized"""
    manager = TrelloConnect()
    # New implementation uses individual attributes instead of dict
    assert hasattr(manager, 'label_remote')
    assert hasattr(manager, 'label_hybrid')
    assert hasattr(manager, 'label_onsite')