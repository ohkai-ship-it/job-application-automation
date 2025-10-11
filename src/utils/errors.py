"""Central exception types for the application."""

from __future__ import annotations


class JobAppError(Exception):
    """Base error for the job application automation app."""


class ScraperError(JobAppError):
    """Raised when scraping fails in a recoverable way."""


class TrelloError(JobAppError):
    """Raised when Trello API operations fail."""


class AIGenerationError(JobAppError):
    """Raised when cover letter generation fails."""


class DocumentError(JobAppError):
    """Raised for DOCX/PDF generation/conversion errors."""
