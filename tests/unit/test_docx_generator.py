"""
Unit tests for document generation
"""
import pytest
import os
from src.docx_generator import WordCoverLetterGenerator

def test_template_replacement():
    """Test template placeholder replacement"""
    generator = WordCoverLetterGenerator()
    
    test_job_data = {
        'company_name': 'Test Corp',
        'job_title': 'Python Developer',
        'location': 'Berlin',
        'company_address': 'Test Street 123, 12345 Berlin'
    }
    
    test_letter = "This is a test cover letter body text."
    output_path = "output/cover_letters/test_template.docx"
    
    # Generate document
    result_path = generator.generate_from_template(
        test_letter,
        test_job_data,
        output_path,
        'english'
    )
    
    # Verify file was created
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0