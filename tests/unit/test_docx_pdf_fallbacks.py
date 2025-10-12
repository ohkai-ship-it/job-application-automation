import os
import types
import builtins
import importlib
import sys
import pytest

from src.docx_generator import WordCoverLetterGenerator
from src.pdf_generator import CoverLetterPDF
from src.utils.errors import DocumentError


@pytest.fixture
def sample_job_data():
    return {
        'company_name': 'Fallback Corp',
        'job_title': 'QA Engineer',
        'location': 'Düsseldorf',
        'company_address': 'Fallback Str. 1, 40235 Düsseldorf'
    }


def test_docx_template_missing_fallback(tmp_path, sample_job_data):
    gen = WordCoverLetterGenerator(template_path_de='data/does_not_exist_de.docx', template_path_en='data/does_not_exist_en.docx')
    output = tmp_path / 'fallback.docx'

    result = gen.generate_from_template(
        cover_letter_text='Body text for fallback path.',
        job_data=sample_job_data,
        output_path=str(output),
        language='english'
    )

    assert os.path.exists(result)
    assert os.path.getsize(result) > 0


def test_convert_to_pdf_returns_none_when_docx2pdf_missing(tmp_path, monkeypatch):
    gen = WordCoverLetterGenerator()
    docx_file = tmp_path / 'file.docx'
    # create a minimal docx using basic generator
    gen._generate_basic_docx('Hello', {'company_name': 'X', 'job_title': 'Y'}, str(docx_file), 'english')

    # Ensure importing docx2pdf raises ImportError
    def fake_import(name, *args, **kwargs):
        if name == 'docx2pdf':
            raise ImportError('docx2pdf not installed')
        return orig_import(name, *args, **kwargs)

    orig_import = builtins.__import__
    monkeypatch.setattr(builtins, '__import__', fake_import)

    pdf_path = gen.convert_to_pdf(str(docx_file))
    assert pdf_path is None


def test_pdf_generator_raises_documenterror_on_build_failure(tmp_path, monkeypatch, sample_job_data):
    pdfgen = CoverLetterPDF()
    output = tmp_path / 'broken.pdf'

    # Monkeypatch SimpleDocTemplate to raise on build
    class FakeDoc:
        def __init__(self, *a, **k):
            pass
        def build(self, story):
            raise RuntimeError('build failed')

    import src.pdf_generator as pdf_module
    monkeypatch.setattr(pdf_module, 'SimpleDocTemplate', FakeDoc)

    with pytest.raises(DocumentError):
        pdfgen.generate_pdf('text', sample_job_data, str(output))
