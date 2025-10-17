"""
Unit tests for TrelloConnect job_data enrichment
"""
import pytest
from src.trello_connect import TrelloConnect


def test_enrich_job_data_detects_german():
    """Test that German language is detected correctly"""
    tc = TrelloConnect()
    job_data = {
        'job_description': 'Wir suchen einen Entwickler für unsere Team. Sie arbeiten mit modernen Technologien und entwickeln innovative Lösungen.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['language'] == 'DE'


def test_enrich_job_data_detects_english():
    """Test that English language is detected correctly"""
    tc = TrelloConnect()
    job_data = {
        'job_description': 'We are looking for a developer to join our team. You will work with modern technologies and develop innovative solutions.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['language'] == 'EN'


def test_enrich_job_data_preserves_existing_language():
    """Test that existing language field is not overwritten"""
    tc = TrelloConnect()
    job_data = {
        'language': 'FR',
        'job_description': 'We are looking for a developer.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['language'] == 'FR'


def test_enrich_job_data_detects_junior_seniority():
    """Test junior seniority detection"""
    tc = TrelloConnect()
    job_data = {
        'job_title': 'Junior Software Engineer',
        'job_description': 'Entry level position for fresh graduates.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['seniority'] == 'junior'


def test_enrich_job_data_detects_senior_seniority():
    """Test senior seniority detection"""
    tc = TrelloConnect()
    job_data = {
        'job_title': 'Senior Software Engineer',
        'job_description': 'Expert level position with 5+ years experience.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['seniority'] == 'senior'


def test_enrich_job_data_detects_lead_seniority():
    """Test lead seniority detection"""
    tc = TrelloConnect()
    job_data = {
        'job_title': 'Lead Developer',
        'job_description': 'Head of development team, principal engineer.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['seniority'] == 'lead'


def test_enrich_job_data_defaults_to_mid_seniority():
    """Test default mid seniority when no indicators found"""
    tc = TrelloConnect()
    job_data = {
        'job_title': 'Software Engineer',
        'job_description': 'Developer position with good experience.'
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['seniority'] == 'mid'


def test_enrich_job_data_normalizes_remote_work_mode():
    """Test remote work mode normalization"""
    tc = TrelloConnect()
    
    # Test "remote/homeoffice" -> "remote"
    job_data1 = {'work_mode': 'remote/homeoffice'}
    assert tc._enrich_job_data(job_data1)['work_mode'] == 'remote'
    
    # Test "Homeoffice möglich" -> "remote"
    job_data2 = {'work_mode': 'Homeoffice möglich'}
    assert tc._enrich_job_data(job_data2)['work_mode'] == 'remote'


def test_enrich_job_data_normalizes_hybrid_work_mode():
    """Test hybrid work mode normalization"""
    tc = TrelloConnect()
    
    job_data = {'work_mode': 'remote/homeoffice hybrid'}
    assert tc._enrich_job_data(job_data)['work_mode'] == 'hybrid'


def test_enrich_job_data_normalizes_onsite_work_mode():
    """Test onsite work mode normalization"""
    tc = TrelloConnect()
    
    # Test "office" -> "onsite"
    job_data1 = {'work_mode': 'office'}
    assert tc._enrich_job_data(job_data1)['work_mode'] == 'onsite'
    
    # Test "vor ort" -> "onsite"
    job_data2 = {'work_mode': 'vor ort'}
    assert tc._enrich_job_data(job_data2)['work_mode'] == 'onsite'


def test_enrich_job_data_defaults_work_mode_to_onsite():
    """Test default work mode when not specified"""
    tc = TrelloConnect()
    
    job_data = {'job_title': 'Developer'}
    enriched = tc._enrich_job_data(job_data)
    assert enriched['work_mode'] == 'onsite'


def test_enrich_job_data_preserves_existing_fields():
    """Test that enrichment doesn't overwrite existing seniority/language/work_mode"""
    tc = TrelloConnect()
    job_data = {
        'language': 'DE',
        'seniority': 'senior',
        'work_mode': 'hybrid',
        'job_title': 'Junior Developer',  # would normally detect as junior
        'job_description': 'We are looking for...'  # would normally detect as EN
    }
    
    enriched = tc._enrich_job_data(job_data)
    assert enriched['language'] == 'DE'
    assert enriched['seniority'] == 'senior'
    assert enriched['work_mode'] == 'hybrid'


def test_enrich_job_data_is_non_destructive():
    """Test that original job_data dict is not modified"""
    tc = TrelloConnect()
    original = {'job_title': 'Developer'}
    original_copy = original.copy()
    
    enriched = tc._enrich_job_data(original)
    
    # Original should be unchanged
    assert original == original_copy
    # Enriched should have new fields
    assert 'seniority' in enriched
    assert 'language' in enriched or enriched.get('job_description') is None
