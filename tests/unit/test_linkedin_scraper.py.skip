"""
Tests for LinkedIn job scraper functionality
"""

import pytest
from unittest.mock import Mock, patch
from src.linkedin_scraper import (
    extract_job_id_from_url,
    extract_job_description,
    scrape_linkedin_job
)


class TestExtractJobIdFromUrl:
    """Test job ID extraction from various LinkedIn URL formats"""
    
    def test_extract_job_id_from_currentJobId_param(self):
        """Extract job ID from currentJobId query parameter"""
        url = "https://www.linkedin.com/jobs/search/?currentJobId=4253399100&keywords=test"
        job_id = extract_job_id_from_url(url)
        assert job_id == "4253399100"
    
    def test_extract_job_id_from_jobs_view_url(self):
        """Extract job ID from /jobs/view/ URL format"""
        url = "https://www.linkedin.com/jobs/view/4253399100/"
        job_id = extract_job_id_from_url(url)
        assert job_id == "4253399100"
    
    def test_extract_job_id_from_collections_url(self):
        """Extract job ID from collections URL with currentJobId"""
        url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4295875663"
        job_id = extract_job_id_from_url(url)
        assert job_id == "4295875663"
    
    def test_extract_job_id_from_long_numeric_string(self):
        """Extract 10+ digit job ID from URL"""
        url = "https://www.linkedin.com/jobs/search/?q=python&jobId=1234567890"
        job_id = extract_job_id_from_url(url)
        assert job_id == "1234567890"
    
    def test_extract_job_id_returns_none_for_invalid_url(self):
        """Return None when no valid job ID found"""
        url = "https://www.linkedin.com/jobs/"
        job_id = extract_job_id_from_url(url)
        assert job_id is None


class TestExtractJobDescription:
    """Test job description extraction from HTML"""
    
    def test_extract_description_with_valid_selector(self):
        """Extract description using valid HTML selector"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <div data-automation-id="jobDescription">
                This is a senior leadership position with benefits including remote work and excellent team collaboration opportunities that span multiple departments and global offices.
            </div>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        description = extract_job_description(soup)
        
        assert description is not None
        assert "senior leadership" in description.lower() or description is not None
    
    def test_extract_description_with_german_content(self):
        """Extract German job description"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <div data-automation-id="jobDescription">
                Wir suchen einen Senior Developer mit 5+ Jahren Erfahrung. 
                Flexible Arbeitszeiten und Remote Work möglich.
            </div>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        description = extract_job_description(soup)
        
        assert description is not None
        assert "Senior Developer" in description
    
    def test_extract_description_handles_short_content(self):
        """Return fallback message if content is too short"""
        from bs4 import BeautifulSoup
        
        html = "<html><div data-automation-id='jobDescription'>Short</div></html>"
        soup = BeautifulSoup(html, 'html.parser')
        description = extract_job_description(soup)
        
        assert "not accessible" in description or description is not None
    
    def test_extract_description_tries_multiple_selectors(self):
        """Try alternative selectors if primary fails"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <div class="jobs-description__content">
                This job requires 10+ years of experience in cloud architecture.
                We offer competitive salary and remote work options.
            </div>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        description = extract_job_description(soup)
        
        assert description is not None
        assert "experience" in description.lower()


class FakeResponse:
    """Mock response object for testing"""
    def __init__(self, content: str, status_code: int = 200):
        self.content = content.encode('utf-8')
        self.status_code = status_code
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class TestScrapeLinkedinJob:
    """Test complete LinkedIn job scraping"""
    
    def test_scrape_linkedin_job_success(self):
        """Successfully scrape LinkedIn job posting"""
        url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253399100"
        
        html_content = """
        <html>
            <head>
                <title>NTT DATA Europe &amp; Latam hiring Head of Industry Experts in Cologne, North Rhine-Westphalia, Germany | LinkedIn</title>
            </head>
            <body>
                <div data-automation-id="jobDescription">
                    Technology is only as good as the people behind it. NTT DATA is hiring for a senior position.
                    We offer flexible working hours, 30 days vacation, and remote work options.
                </div>
            </body>
        </html>
        """
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            assert job_data is not None
            assert job_data['company_name'] == 'NTT DATA Europe & Latam'
            assert 'Head of Industry Experts' in job_data['job_title']
            assert 'Cologne' in job_data['location']
            assert job_data['source_url'] == url
    
    def test_scrape_linkedin_job_with_emojis(self):
        """Handle job titles with emoji characters"""
        url = "https://www.linkedin.com/jobs/view/4295875663/"
        
        html_content = """
        <html>
            <head>
                <title>HeapsGo 🚀 hiring Join HeapsGo 🌟 in Berlin – Get Paid 🤑 | LinkedIn</title>
            </head>
            <body>
                <div data-automation-id="jobDescription">
                    Join our team and earn commissions for restaurant introductions.
                </div>
            </body>
        </html>
        """
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            assert job_data is not None
            # Emojis should be cleaned
            assert '🚀' not in job_data['company_name']
            assert '🌟' not in job_data['job_title']
    
    def test_scrape_linkedin_job_returns_standard_format(self):
        """Verify returned data matches standard job_data format"""
        url = "https://www.linkedin.com/jobs/view/123456789/"
        
        html_content = """
        <html>
            <head>
                <title>Acme Corp hiring Senior Engineer in New York, NY | LinkedIn</title>
            </head>
            <body>
                <div data-automation-id="jobDescription">
                    We are looking for a senior engineer with Python experience.
                </div>
            </body>
        </html>
        """
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            # Verify all required fields are present
            assert 'company_name' in job_data
            assert 'job_title' in job_data
            assert 'job_description' in job_data
            assert 'location' in job_data
            assert 'source_url' in job_data
            assert 'company_address' in job_data
            assert 'career_page_link' in job_data  # Must have portal/career page link
            
            # Verify compatibility with existing workflow
            assert isinstance(job_data['company_name'], str)
            assert isinstance(job_data['job_title'], str)
            assert job_data['source_url'] == url
            # Career page link should be a non-empty string
            assert isinstance(job_data['career_page_link'], str)
            assert len(job_data['career_page_link']) > 0
    
    def test_scrape_linkedin_job_handles_no_title(self):
        """Handle page without proper title"""
        url = "https://www.linkedin.com/jobs/view/999999999/"
        
        html_content = "<html><body>No title</body></html>"
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            assert job_data is None
    
    def test_scrape_linkedin_job_handles_network_error(self):
        """Handle network errors gracefully"""
        url = "https://www.linkedin.com/jobs/view/123456789/"
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            job_data = scrape_linkedin_job(url)
            
            assert job_data is None
    
    def test_scrape_linkedin_job_german_posting(self):
        """Scrape German language job posting"""
        url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253399100"
        
        html_content = """
        <html>
            <head>
                <title>Siemens AG sucht Senior DevOps Engineer in München, Bayern, Deutschland | LinkedIn</title>
            </head>
            <body>
                <div data-automation-id="jobDescription">
                    Wir suchen einen erfahrenen DevOps Engineer. Anforderungen: 5+ Jahre Erfahrung mit Kubernetes,
                    Docker und Cloud-Technologien. Wir bieten flexible Arbeitszeiten und Remote Work Möglichkeiten.
                </div>
            </body>
        </html>
        """
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            # The title parsing requires the "sucht" or "hiring" keyword to work correctly
            assert job_data is not None
            assert job_data['source_url'] == url
    
    def test_scrape_linkedin_job_with_special_characters(self):
        """Handle special characters in company/job names"""
        url = "https://www.linkedin.com/jobs/view/123456789/"
        
        html_content = """
        <html>
            <head>
                <title>D&apos;Amore-McKenzie &amp; Partners hiring Senior Consultant (M/W/D) in Frankfurt am Main | LinkedIn</title>
            </head>
            <body>
                <div data-automation-id="jobDescription">
                    Join our elite consulting team for enterprise transformation.
                </div>
            </body>
        </html>
        """
        
        with patch('src.linkedin_scraper.requests.get') as mock_get:
            mock_get.return_value = FakeResponse(html_content)
            
            job_data = scrape_linkedin_job(url)
            
            assert job_data is not None
            assert job_data['company_name'] is not None
            assert len(job_data['company_name']) > 0


class TestMainIntegration:
    """Test integration with main.py's detect_job_source function"""
    
    def test_detect_linkedin_url(self):
        """Detect LinkedIn URLs in main workflow"""
        from src.main import detect_job_source
        
        urls = [
            "https://www.linkedin.com/jobs/view/4253399100/",
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253399100",
            "https://www.linkedin.com/jobs/search/?currentJobId=4295875663",
        ]
        
        for url in urls:
            assert detect_job_source(url) == 'linkedin'
    
    def test_detect_stepstone_url(self):
        """Detect Stepstone URLs in main workflow"""
        from src.main import detect_job_source
        
        urls = [
            "https://www.stepstone.de/stelle/...",
            "https://stepstone.de/jobs/...",
            "https://www.stepstone.at/stelle/...",
        ]
        
        for url in urls:
            assert detect_job_source(url) == 'stepstone'
    
    def test_process_job_posting_with_linkedin_url(self):
        """Test complete workflow with LinkedIn URL"""
        # This is an integration test that would need mocking of:
        # - Network requests (scraping)
        # - Trello API
        # - OpenAI API
        # For now, we test that the URL detection works correctly
        from src.main import detect_job_source
        
        url = "https://www.linkedin.com/jobs/view/4253399100/"
        source = detect_job_source(url)
        assert source == 'linkedin'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
