"""
Comprehensive tests for database duplicate detection logic
Tests all combinations of duplicate detection:
- Stage 1: URL hash matching (exact duplicates)
- Stage 2: Semantic matching (reposted/cross-source duplicates)
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import pytest
from src.database import ApplicationDB
from datetime import datetime


@pytest.fixture
def temp_db():
    """Create a temporary test database"""
    db_path = Path("test_duplicate_detection.db")
    
    # Remove if exists
    if db_path.exists():
        db_path.unlink()
    
    db = ApplicationDB(db_path=str(db_path))
    yield db
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


class TestDuplicateDetectionStage1:
    """Tests for Stage 1: URL Hash matching"""
    
    def test_no_duplicate_empty_database(self, temp_db):
        """Test that no duplicate is found in empty database"""
        url = "https://www.linkedin.com/jobs/view/1234567890/"
        is_duplicate, job_data, method = temp_db.check_duplicate(url)
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'
    
    def test_exact_url_duplicate_detection(self, temp_db):
        """Test detection of exact URL duplicates"""
        url = "https://www.linkedin.com/jobs/view/1234567890/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url,
            company_name='Test Company',
            job_title='Test Position',
            trello_card_url='https://trello.com/c/test123'
        )
        
        # Check duplicate with same URL
        is_duplicate, job_data, method = temp_db.check_duplicate(url)
        
        assert is_duplicate is True
        assert job_data is not None
        assert method == 'url_hash'
        assert job_data['company_name'] == 'Test Company'
        assert job_data['job_title'] == 'Test Position'
    
    def test_multiple_different_urls(self, temp_db):
        """Test that different URLs are not flagged as duplicates"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.linkedin.com/jobs/view/2222222222/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Company A',
            job_title='Position A',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Insert second job with different URL
        temp_db.save_processed_job(
            source_url=url2,
            company_name='Company B',
            job_title='Position B',
            trello_card_url='https://trello.com/c/test2'
        )
        
        # Check first URL - should be duplicate (exists)
        is_dup1, job1, method1 = temp_db.check_duplicate(url1)
        assert is_dup1 is True
        assert method1 == 'url_hash'
        assert job1['company_name'] == 'Company A'
        
        # Check second URL - should be duplicate (exists)
        is_dup2, job2, method2 = temp_db.check_duplicate(url2)
        assert is_dup2 is True
        assert method2 == 'url_hash'
        assert job2['company_name'] == 'Company B'
        
        # Check third URL - should be no duplicate
        url3 = "https://www.linkedin.com/jobs/view/3333333333/"
        is_dup3, job3, method3 = temp_db.check_duplicate(url3)
        assert is_dup3 is False
        assert job3 is None
        assert method3 == 'none'


class TestDuplicateDetectionStage2:
    """Tests for Stage 2: Semantic matching"""
    
    def test_semantic_duplicate_same_company_and_title(self, temp_db):
        """Test detection of semantic duplicates (reposted job on different URL)"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check second URL (different URL, same company & title)
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Acme Corp',
            job_title='Senior Python Developer'
        )
        
        assert is_duplicate is True
        assert job_data is not None
        assert method == 'semantic'
        assert job_data['source_url'] == url1  # Should return original URL
    
    def test_semantic_no_duplicate_different_title(self, temp_db):
        """Test that different job titles are not flagged as duplicates"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with different title
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Acme Corp',
            job_title='Junior Python Developer'  # Different title
        )
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'
    
    def test_semantic_no_duplicate_different_company(self, temp_db):
        """Test that different companies are not flagged as duplicates"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with different company
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Beta Inc',  # Different company
            job_title='Senior Python Developer'
        )
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'
    
    def test_semantic_duplicate_case_insensitive(self, temp_db):
        """Test that semantic matching is case-insensitive"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with different case
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='ACME CORP',  # Upper case
            job_title='senior python developer'  # Lower case
        )
        
        assert is_duplicate is True
        assert job_data is not None
        assert method == 'semantic'
    
    def test_semantic_duplicate_with_whitespace(self, temp_db):
        """Test that semantic matching handles extra whitespace"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with extra whitespace
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='  Acme Corp  ',  # Extra spaces
            job_title='  Senior Python Developer  '  # Extra spaces
        )
        
        assert is_duplicate is True
        assert job_data is not None
        assert method == 'semantic'
    
    def test_semantic_check_skipped_without_company_name(self, temp_db):
        """Test that semantic check is skipped if company_name not provided"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check without company_name (only job_title)
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name=None,  # Not provided
            job_title='Senior Python Developer'
        )
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'
    
    def test_semantic_check_skipped_without_job_title(self, temp_db):
        """Test that semantic check is skipped if job_title not provided"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        url2 = "https://www.stepstone.de/jobs/1234567/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Corp',
            job_title='Senior Python Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check without job_title (only company_name)
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Acme Corp',
            job_title=None  # Not provided
        )
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'


class TestDuplicateDetectionCombinations:
    """Tests for all possible combinations of duplicate detection scenarios"""
    
    def test_scenario_1_first_occurrence(self, temp_db):
        """Scenario 1: First time processing a job URL"""
        url = "https://www.linkedin.com/jobs/view/9999999999/"
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url,
            company_name='New Company',
            job_title='New Position'
        )
        
        assert is_duplicate is False
        assert job_data is None
        assert method == 'none'
    
    def test_scenario_2_exact_duplicate_same_url(self, temp_db):
        """Scenario 2: Processing same URL again (exact duplicate)"""
        url = "https://www.linkedin.com/jobs/view/5555555555/"
        
        # First insert
        temp_db.save_processed_job(
            source_url=url,
            company_name='Company X',
            job_title='Position X',
            trello_card_url='https://trello.com/c/testX'
        )
        
        # Try to process same URL again
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url,
            company_name='Company X',
            job_title='Position X'
        )
        
        # Should detect via Stage 1 (URL hash)
        assert is_duplicate is True
        assert method == 'url_hash'
    
    def test_scenario_3_reposted_job_different_url(self, temp_db):
        """Scenario 3: Job reposted on another source (different URL, same company/title)"""
        url1 = "https://www.linkedin.com/jobs/view/6666666666/"
        url2 = "https://www.stepstone.de/jobs/9876543/"
        
        # Insert from LinkedIn
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Tech Solutions GmbH',
            job_title='DevOps Engineer',
            trello_card_url='https://trello.com/c/linkedincard'
        )
        
        # Now see the same job on Stepstone
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Tech Solutions GmbH',
            job_title='DevOps Engineer'
        )
        
        # Should detect via Stage 2 (semantic match)
        assert is_duplicate is True
        assert method == 'semantic'
        assert job_data['source_url'] == url1
    
    def test_scenario_4_similar_company_different_title(self, temp_db):
        """Scenario 4: Similar company but different job title (not a duplicate)"""
        url1 = "https://www.linkedin.com/jobs/view/7777777777/"
        url2 = "https://www.stepstone.de/jobs/5555555/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Acme Consulting',
            job_title='Senior Consultant',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check second job with similar company but different title
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Acme Consulting',
            job_title='Junior Developer'  # Different title
        )
        
        assert is_duplicate is False
        assert method == 'none'
    
    def test_scenario_5_same_title_different_company(self, temp_db):
        """Scenario 5: Same job title but different company (not a duplicate)"""
        url1 = "https://www.linkedin.com/jobs/view/8888888888/"
        url2 = "https://www.stepstone.de/jobs/3333333/"
        
        # Insert first job
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Company Alpha',
            job_title='Software Architect',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check second job with different company but same title
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url2,
            company_name='Company Beta',  # Different company
            job_title='Software Architect'
        )
        
        assert is_duplicate is False
        assert method == 'none'
    
    def test_scenario_6_multiple_jobs_correct_match(self, temp_db):
        """Scenario 6: Multiple jobs in database, correct one matched"""
        # Insert 3 different jobs
        temp_db.save_processed_job(
            source_url='https://linkedin.com/1',
            company_name='Company A',
            job_title='Position 1',
            trello_card_url='https://trello.com/c/test1'
        )
        
        temp_db.save_processed_job(
            source_url='https://linkedin.com/2',
            company_name='Company B',
            job_title='Position 2',
            trello_card_url='https://trello.com/c/test2'
        )
        
        temp_db.save_processed_job(
            source_url='https://linkedin.com/3',
            company_name='Company C',
            job_title='Position 3',
            trello_card_url='https://trello.com/c/test3'
        )
        
        # Check semantic match for middle one
        is_duplicate, job_data, method = temp_db.check_duplicate(
            'https://stepstone.de/new',
            company_name='Company B',
            job_title='Position 2'
        )
        
        assert is_duplicate is True
        assert method == 'semantic'
        assert job_data['source_url'] == 'https://linkedin.com/2'
    
    def test_scenario_7_url_hash_takes_precedence(self, temp_db):
        """Scenario 7: If URL hash matches, Stage 1 returns immediately"""
        url = "https://www.linkedin.com/jobs/view/4444444444/"
        
        # Insert job
        temp_db.save_processed_job(
            source_url=url,
            company_name='Original Company',
            job_title='Original Position',
            trello_card_url='https://trello.com/c/original'
        )
        
        # Check with WRONG company/title but SAME URL
        is_duplicate, job_data, method = temp_db.check_duplicate(
            url,
            company_name='Different Company',  # Wrong
            job_title='Different Position'  # Wrong
        )
        
        # Should match on URL hash and return original data
        assert is_duplicate is True
        assert method == 'url_hash'
        assert job_data['company_name'] == 'Original Company'
    
    def test_scenario_8_return_values_structure(self, temp_db):
        """Scenario 8: Verify return value structure is always correct"""
        url = "https://www.linkedin.com/jobs/view/1234567890/"
        
        # Test no duplicate case
        result = temp_db.check_duplicate(url)
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert result[1] is None
        assert isinstance(result[2], str)
        assert result[2] == 'none'
        
        # Insert job and test duplicate case
        temp_db.save_processed_job(
            source_url=url,
            company_name='Test Co',
            job_title='Test Job',
            trello_card_url='https://trello.com/c/test'
        )
        
        result = temp_db.check_duplicate(url)
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], dict)
        assert isinstance(result[2], str)
        assert result[2] in ['url_hash', 'semantic', 'none']


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_empty_company_name_not_matched_semantically(self, temp_db):
        """Test that empty company names don't match via semantic detection"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        
        # Insert job with empty company name
        temp_db.save_processed_job(
            source_url=url1,
            company_name='',
            job_title='Position',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Try to match with another empty company
        # This should NOT match semantically (both empty strings)
        # because matching on empty data is not useful
        is_duplicate, _, method = temp_db.check_duplicate(
            'https://www.linkedin.com/jobs/view/2222222222/',
            company_name='',
            job_title='Position'
        )
        
        # Should not match - empty company names shouldn't be semantically matched
        assert is_duplicate is False
        assert method == 'none'
    
    def test_special_characters_in_company_name(self, temp_db):
        """Test that special characters are handled correctly"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        
        # Insert job with special characters
        temp_db.save_processed_job(
            source_url=url1,
            company_name="O'Reilly & Associates",
            job_title='Senior C++ Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with same special characters
        is_duplicate, _, method = temp_db.check_duplicate(
            'https://www.linkedin.com/jobs/view/2222222222/',
            company_name="O'Reilly & Associates",
            job_title='Senior C++ Developer'
        )
        
        assert is_duplicate is True
        assert method == 'semantic'
    
    def test_unicode_characters_in_company_name(self, temp_db):
        """Test that Unicode characters are handled correctly"""
        url1 = "https://www.linkedin.com/jobs/view/1111111111/"
        
        # Insert job with Unicode characters
        temp_db.save_processed_job(
            source_url=url1,
            company_name='Müller & Söhne GmbH',
            job_title='Developer',
            trello_card_url='https://trello.com/c/test1'
        )
        
        # Check with same Unicode
        is_duplicate, _, method = temp_db.check_duplicate(
            'https://www.linkedin.com/jobs/view/2222222222/',
            company_name='Müller & Söhne GmbH',
            job_title='Developer'
        )
        
        assert is_duplicate is True
        assert method == 'semantic'
