"""
File management utilities for job application automation.
Handles deletion and cleanup of generated files.
"""

import os
from pathlib import Path
from typing import Dict
from utils.log_config import get_logger

logger = get_logger(__name__)


def delete_generated_files(docx_file: str = None, pdf_file: str = None) -> Dict[str, bool]:
    """
    Delete generated cover letter files.
    
    Args:
        docx_file: Path to DOCX file
        pdf_file: Path to PDF file
    
    Returns:
        Dict with deletion status: {'docx': bool, 'pdf': bool, 'all_deleted': bool}
    """
    results = {'docx': False, 'pdf': False}
    
    # Delete DOCX if provided
    if docx_file:
        try:
            if os.path.exists(docx_file):
                os.remove(docx_file)
                logger.info(f"Deleted DOCX file: {docx_file}")
                results['docx'] = True
            else:
                logger.warning(f"DOCX file not found (already deleted?): {docx_file}")
        except Exception as e:
            logger.error(f"Failed to delete DOCX file {docx_file}: {e}")
    
    # Delete PDF if provided
    if pdf_file:
        try:
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
                logger.info(f"Deleted PDF file: {pdf_file}")
                results['pdf'] = True
            else:
                logger.warning(f"PDF file not found (already deleted?): {pdf_file}")
        except Exception as e:
            logger.error(f"Failed to delete PDF file {pdf_file}: {e}")
    
    results['all_deleted'] = results['docx'] or results['pdf'] or (not docx_file and not pdf_file)
    return results
