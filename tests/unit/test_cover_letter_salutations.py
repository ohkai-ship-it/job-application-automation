"""
Unit tests for cover letter salutation and valediction generation.
Tests formality detection, salutation/valediction generation, and integration.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from src.cover_letter import CoverLetterGenerator


@pytest.fixture
def generator():
    """Create a CoverLetterGenerator instance for testing."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        with patch('src.cover_letter.OpenAI'):
            gen = CoverLetterGenerator()
            gen.cv_de = "Deutscher Lebenslauf"
            gen.cv_en = "English CV"
            return gen


class TestFormalityDetection:
    """Tests for detect_german_formality method."""
    
    def test_detect_formality_informal_with_du(self, generator):
        """Test detection of informal German using 'du'."""
        job_desc = "Wir suchen dich! Du wirst mit unserem Team arbeiten und deine Ideen einbringen."
        assert generator.detect_german_formality(job_desc) == 'informal'
    
    def test_detect_formality_informal_with_dein(self, generator):
        """Test detection of informal German using 'dein'."""
        job_desc = "Bring deine Erfahrung ein und gestalte mit uns die Zukunft."
        assert generator.detect_german_formality(job_desc) == 'informal'
    
    def test_detect_formality_formal_with_sie(self, generator):
        """Test detection of formal German using 'Sie'."""
        job_desc = "Sie werden in unserem Team arbeiten und Ihre Expertise einbringen."
        assert generator.detect_german_formality(job_desc) == 'formal'
    
    def test_detect_formality_formal_with_ihnen(self, generator):
        """Test detection of formal German using 'Ihnen'."""
        job_desc = "Wir bieten Ihnen eine spannende Position in unserem Unternehmen."
        assert generator.detect_german_formality(job_desc) == 'formal'
    
    def test_detect_formality_default_formal(self, generator):
        """Test that default is formal when no clear indicators."""
        job_desc = "Das Unternehmen sucht einen Entwickler für das Team."
        assert generator.detect_german_formality(job_desc) == 'formal'
    
    def test_detect_formality_empty_string(self, generator):
        """Test handling of empty job description."""
        assert generator.detect_german_formality('') == 'formal'
    
    def test_detect_formality_mixed_but_more_formal(self, generator):
        """Test when both forms present but formal dominates."""
        job_desc = "Sie werden in unserem Team arbeiten. Wir bieten Ihnen tolle Möglichkeiten. Du kannst gerne fragen."
        assert generator.detect_german_formality(job_desc) == 'formal'


class TestSalutationGeneration:
    """Tests for generate_salutation method."""
    
    def test_salutation_german_formal_with_contact_herr(self, generator):
        """Test German formal salutation with male contact."""
        job_data = {
            'company_name': 'Acme GmbH',
            'contact_person': {'name': 'Herr Schmidt'}
        }
        result = generator.generate_salutation(job_data, 'german', 'formal', 'mid')
        assert result == 'Sehr geehrter Herr Schmidt,'
    
    def test_salutation_german_formal_with_contact_frau(self, generator):
        """Test German formal salutation with female contact."""
        job_data = {
            'company_name': 'Acme GmbH',
            'contact_person': {'name': 'Frau Müller'}
        }
        result = generator.generate_salutation(job_data, 'german', 'formal', 'mid')
        assert result == 'Sehr geehrte Frau Müller,'
    
    def test_salutation_german_formal_without_contact(self, generator):
        """Test German formal salutation without contact person."""
        job_data = {'company_name': 'Acme GmbH'}
        result = generator.generate_salutation(job_data, 'german', 'formal', 'mid')
        assert result == 'Sehr geehrtes Acme GmbH-Team,'
    
    def test_salutation_german_informal_with_contact(self, generator):
        """Test German informal salutation with contact."""
        job_data = {
            'company_name': 'StartupCo',
            'contact_person': {'name': 'Max Mustermann'}
        }
        result = generator.generate_salutation(job_data, 'german', 'informal', 'junior')
        assert result == 'Hallo Max,'
    
    def test_salutation_german_informal_without_contact_junior(self, generator):
        """Test German informal salutation without contact (junior position)."""
        job_data = {'company_name': 'StartupCo'}
        result = generator.generate_salutation(job_data, 'german', 'informal', 'junior')
        assert result == 'Hallo StartupCo-Team,'
    
    def test_salutation_german_informal_without_contact_senior(self, generator):
        """Test German informal salutation without contact (senior position)."""
        job_data = {'company_name': 'StartupCo'}
        result = generator.generate_salutation(job_data, 'german', 'informal', 'senior')
        assert result == 'Liebes StartupCo-Team,'
    
    def test_salutation_english_with_contact(self, generator):
        """Test English salutation with contact person."""
        job_data = {
            'company_name': 'Tech Corp',
            'contact_person': {'name': 'John Smith'}
        }
        result = generator.generate_salutation(job_data, 'english', 'formal', 'mid')
        assert result == 'Dear John Smith,'
    
    def test_salutation_english_without_contact_executive(self, generator):
        """Test English salutation without contact (executive position)."""
        job_data = {'company_name': 'Tech Corp'}
        result = generator.generate_salutation(job_data, 'english', 'formal', 'executive')
        assert result == 'Dear Hiring Manager,'
    
    def test_salutation_english_without_contact_junior(self, generator):
        """Test English salutation without contact (junior position)."""
        job_data = {'company_name': 'Tech Corp'}
        result = generator.generate_salutation(job_data, 'english', 'formal', 'junior')
        assert result == 'Dear Tech Corp Hiring Team,'


class TestValedictionGeneration:
    """Tests for generate_valediction method."""
    
    def test_valediction_german_formal(self, generator):
        """Test German formal valediction."""
        result = generator.generate_valediction('german', 'formal', 'mid')
        assert result == 'Mit freundlichen Grüßen'
    
    def test_valediction_german_informal_junior(self, generator):
        """Test German informal valediction for junior position."""
        result = generator.generate_valediction('german', 'informal', 'junior')
        assert result == 'Viele Grüße'
    
    def test_valediction_german_informal_senior(self, generator):
        """Test German informal valediction for senior position."""
        result = generator.generate_valediction('german', 'informal', 'senior')
        assert result == 'Beste Grüße'
    
    def test_valediction_english_executive(self, generator):
        """Test English valediction for executive position."""
        result = generator.generate_valediction('english', 'formal', 'executive')
        assert result == 'Sincerely,'
    
    def test_valediction_english_junior(self, generator):
        """Test English valediction for junior position."""
        result = generator.generate_valediction('english', 'informal', 'junior')
        assert result == 'Best,'
    
    def test_valediction_english_mid(self, generator):
        """Test English valediction for mid-level position."""
        result = generator.generate_valediction('english', 'formal', 'mid')
        assert result == 'Best regards,'


class TestIntegration:
    """Integration tests for complete cover letter generation."""
    
    def test_generate_cover_letter_adds_all_three_parts_to_job_data(self, generator):
        """Test that generate_cover_letter adds salutation, body, and valediction to job_data."""
        job_data = {
            'company_name': 'Test GmbH',
            'job_title': 'Software Engineer',
            'job_description': 'Sie werden in unserem Team arbeiten und innovative Lösungen entwickeln.',
            'location': 'Berlin'
        }
        
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ' '.join(['word'] * 200)  # 200 words
        
        generator.client = MagicMock()
        generator.client.chat.completions.create.return_value = mock_response
        
        # Generate cover letter
        result = generator.generate_cover_letter(job_data)
        
        # Check that all three parts are added to job_data
        assert 'cover_letter_salutation' in job_data
        assert 'cover_letter_body' in job_data
        assert 'cover_letter_valediction' in job_data
        
        # Check that they have appropriate values
        assert 'Sehr geehrtes' in job_data['cover_letter_salutation']
        assert len(job_data['cover_letter_body']) > 0
        assert 'Grüßen' in job_data['cover_letter_valediction']
        
        # Check backward compatibility: returned value is the body
        assert result == job_data['cover_letter_body']
    
    def test_generate_cover_letter_german_informal_with_contact(self, generator):
        """Test informal German cover letter with contact person."""
        job_data = {
            'company_name': 'Startup GmbH',
            'job_title': 'Junior Developer',
            'job_description': 'Du wirst mit unserem Team arbeiten und deine Ideen einbringen können.',
            'location': 'Munich',
            'contact_person': {'name': 'Anna Schmidt'}
        }
        
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ' '.join(['word'] * 200)
        
        generator.client = MagicMock()
        generator.client.chat.completions.create.return_value = mock_response
        
        # Generate
        generator.generate_cover_letter(job_data)
        
        # Check informal salutation
        assert 'Hallo Anna,' == job_data['cover_letter_salutation']
        assert 'Viele Grüße' == job_data['cover_letter_valediction']
        
        # Check that prompt included formality instruction
        call_args = generator.client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        assert 'Du-Form' in prompt
    
    def test_generate_cover_letter_english(self, generator):
        """Test English cover letter generation."""
        job_data = {
            'company_name': 'Tech Corp',
            'job_title': 'Senior Engineer',
            'job_description': 'You will work with our team and lead innovative projects.',
            'location': 'London'
        }
        
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ' '.join(['word'] * 200)
        
        generator.client = MagicMock()
        generator.client.chat.completions.create.return_value = mock_response
        
        # Generate
        generator.generate_cover_letter(job_data)
        
        # Check English salutation and valediction
        assert 'Dear' in job_data['cover_letter_salutation']
        assert job_data['cover_letter_valediction'] in ['Sincerely,', 'Best regards,']
