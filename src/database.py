"""
Database Layer for Job Application Automation
Lightweight SQLite database for duplicate detection and generation tracking.
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from utils.log_config import get_logger

logger = get_logger(__name__)


class ApplicationDB:
    """
    Lightweight database for tracking processed jobs and AI generations.
    
    Purpose:
    - Prevent duplicate processing of the same job URL
    - Track AI generation costs and metadata
    - Link to Trello cards (Trello is the source of truth)
    
    NOT for application status tracking (Trello handles that).
    """
    
    def __init__(self, db_path: str = "data/applications.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not self.db_path.exists():
            logger.info(f"Database not found, will create: {self.db_path}")
            self._create_schema()
        else:
            logger.debug(f"Using existing database: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _create_schema(self):
        """Create database tables if they don't exist."""
        logger.info("Creating database schema...")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: processed_jobs (duplicate detection)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    source_url TEXT NOT NULL UNIQUE,
                    company_name TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cover_letter_generated BOOLEAN DEFAULT 1,
                    trello_card_id TEXT,
                    trello_card_url TEXT,
                    docx_file_path TEXT,
                    notes TEXT
                )
            """)
            
            # Indexes for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_job_id 
                ON processed_jobs(job_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_url 
                ON processed_jobs(source_url)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_processed_at 
                ON processed_jobs(processed_at DESC)
            """)
            
            # Table 2: generation_metadata (AI tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    ai_model TEXT NOT NULL,
                    language TEXT CHECK(language IN ('de', 'en')),
                    word_count INTEGER,
                    generation_cost REAL,
                    prompt_version TEXT,
                    generation_time_seconds REAL,
                    cover_letter_text TEXT,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES processed_jobs(job_id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_job_id 
                ON generation_metadata(job_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_model 
                ON generation_metadata(ai_model)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_generated_at 
                ON generation_metadata(generated_at DESC)
            """)
            
            conn.commit()
            logger.info("Database schema created successfully")
    
    @staticmethod
    def _calculate_job_id(source_url: str) -> str:
        """
        Calculate unique job ID from URL using SHA256 hash.
        
        Args:
            source_url: Job posting URL
            
        Returns:
            SHA256 hash (first 16 characters for readability)
        """
        return hashlib.sha256(source_url.encode()).hexdigest()[:16]
    
    def check_duplicate(self, source_url: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a job URL has already been processed.
        
        Args:
            source_url: Job posting URL to check
            
        Returns:
            Tuple of (is_duplicate, existing_job_data or None)
        """
        job_id = self._calculate_job_id(source_url)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_id, company_name, job_title, processed_at,
                       trello_card_url, docx_file_path
                FROM processed_jobs
                WHERE job_id = ? OR source_url = ?
            """, (job_id, source_url))
            
            row = cursor.fetchone()
            
            if row:
                logger.info(f"Duplicate found: {row['company_name']} - {row['job_title']}")
                return True, dict(row)
            else:
                logger.debug(f"No duplicate found for job_id: {job_id}")
                return False, None
    
    def save_processed_job(
        self,
        source_url: str,
        company_name: str,
        job_title: str,
        trello_card_id: Optional[str] = None,
        trello_card_url: Optional[str] = None,
        docx_file_path: Optional[str] = None,
        notes: Optional[str] = None,
        # AI generation metadata
        ai_model: Optional[str] = None,
        language: Optional[str] = None,
        word_count: Optional[int] = None,
        generation_cost: Optional[float] = None,
        generation_time: Optional[float] = None,
        cover_letter_text: Optional[str] = None,
        prompt_version: Optional[str] = None
    ) -> str:
        """
        Save a processed job to the database.
        
        Args:
            source_url: Job posting URL
            company_name: Company name
            job_title: Job title
            trello_card_id: Trello card ID (optional)
            trello_card_url: Trello card URL (optional)
            docx_file_path: Path to generated DOCX file (optional)
            notes: Additional notes (optional)
            ai_model: AI model used (e.g., "gpt-4o-mini")
            language: Language of cover letter ("de" or "en")
            word_count: Cover letter word count
            generation_cost: Cost in USD
            generation_time: Generation time in seconds
            cover_letter_text: Generated cover letter text
            prompt_version: Prompt version identifier
            
        Returns:
            job_id: Unique job identifier
        """
        job_id = self._calculate_job_id(source_url)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert into processed_jobs
            cursor.execute("""
                INSERT INTO processed_jobs 
                (job_id, source_url, company_name, job_title, 
                 trello_card_id, trello_card_url, docx_file_path, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, source_url, company_name, job_title,
                trello_card_id, trello_card_url, docx_file_path, notes
            ))
            
            # Insert generation metadata if provided
            if ai_model:
                cursor.execute("""
                    INSERT INTO generation_metadata
                    (job_id, ai_model, language, word_count, generation_cost,
                     generation_time_seconds, cover_letter_text, prompt_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id, ai_model, language, word_count, generation_cost,
                    generation_time, cover_letter_text, prompt_version
                ))
            
            conn.commit()
            logger.info(f"Saved job to database: {company_name} - {job_title} (job_id: {job_id})")
            
            return job_id
    
    def get_recent_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently processed jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_id, company_name, job_title, processed_at,
                       trello_card_url, docx_file_path
                FROM processed_jobs
                ORDER BY processed_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job details by job_id.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Job dictionary or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processed_jobs WHERE job_id = ?
            """, (job_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_generation_history(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all AI generations for a specific job (if regenerated multiple times).
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            List of generation metadata dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ai_model, language, word_count, generation_cost,
                       generation_time_seconds, generated_at
                FROM generation_metadata
                WHERE job_id = ?
                ORDER BY generated_at DESC
            """, (job_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_stats(self, period: str = 'all') -> Dict[str, Any]:
        """
        Get AI cost statistics.
        
        Args:
            period: 'all', 'month', 'week', 'day'
            
        Returns:
            Dictionary with cost statistics
        """
        date_filter = {
            'day': "date('now')",
            'week': "date('now', '-7 days')",
            'month': "date('now', 'start of month')",
            'all': "date('1970-01-01')"
        }
        
        where_clause = f"WHERE generated_at >= {date_filter.get(period, date_filter['all'])}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as count,
                    SUM(generation_cost) as total_cost,
                    AVG(generation_cost) as avg_cost,
                    MIN(generation_cost) as min_cost,
                    MAX(generation_cost) as max_cost
                FROM generation_metadata
                {where_clause}
            """)
            
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def search_jobs(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search jobs by company name or job title.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching jobs
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, job_id, company_name, job_title, processed_at,
                       trello_card_url, docx_file_path
                FROM processed_jobs
                WHERE company_name LIKE ? OR job_title LIKE ?
                ORDER BY processed_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_all(self) -> None:
        """
        Clear all records from the database (used for cancellation/cleanup).
        
        Deletes all entries from both processed_jobs and generation_metadata tables.
        WARNING: This is destructive and cannot be undone.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete all generation metadata (will cascade from processed_jobs deletion)
                cursor.execute("DELETE FROM generation_metadata")
                
                # Delete all processed jobs
                cursor.execute("DELETE FROM processed_jobs")
                
                conn.commit()
                logger.info("Database cleared: all records removed")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise
    
    def delete_job(self, job_id: str = None, source_url: str = None) -> bool:
        """
        Delete a job record from the database.
        
        Args:
            job_id: Job ID (preferred lookup)
            source_url: Source URL (fallback lookup)
        
        Returns:
            True if deleted, False if not found
        """
        if not job_id and not source_url:
            logger.error("Either job_id or source_url required for deletion")
            return False
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if job_id:
                    cursor.execute("DELETE FROM processed_jobs WHERE job_id = ?", (job_id,))
                else:
                    cursor.execute("DELETE FROM processed_jobs WHERE source_url = ?", (source_url,))
                
                deleted = cursor.rowcount > 0
                conn.commit()
                
                if deleted:
                    logger.info(f"Deleted job from database: {job_id or source_url}")
                else:
                    logger.warning(f"Job not found in database: {job_id or source_url}")
                
                return deleted
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall database statistics.
        
        Returns:
            Dictionary with stats
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total jobs processed
            cursor.execute("SELECT COUNT(*) as total FROM processed_jobs")
            total_jobs = cursor.fetchone()['total']
            
            # Jobs this week
            cursor.execute("""
                SELECT COUNT(*) as this_week 
                FROM processed_jobs 
                WHERE processed_at >= date('now', '-7 days')
            """)
            jobs_this_week = cursor.fetchone()['this_week']
            
            # Jobs this month
            cursor.execute("""
                SELECT COUNT(*) as this_month 
                FROM processed_jobs 
                WHERE processed_at >= date('now', 'start of month')
            """)
            jobs_this_month = cursor.fetchone()['this_month']
            
            # Total cost
            cursor.execute("""
                SELECT SUM(generation_cost) as total_cost 
                FROM generation_metadata
            """)
            total_cost = cursor.fetchone()['total_cost'] or 0.0
            
            # Top companies
            cursor.execute("""
                SELECT company_name, COUNT(*) as count
                FROM processed_jobs
                GROUP BY company_name
                ORDER BY count DESC
                LIMIT 5
            """)
            top_companies = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_jobs': total_jobs,
                'jobs_this_week': jobs_this_week,
                'jobs_this_month': jobs_this_month,
                'total_ai_cost': round(total_cost, 4),
                'top_companies': top_companies
            }


# Singleton instance
_db_instance: Optional[ApplicationDB] = None


def get_db() -> ApplicationDB:
    """
    Get singleton database instance.
    
    Returns:
        ApplicationDB instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = ApplicationDB()
    return _db_instance


# Testing
if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MODULE TEST")
    print("=" * 80)
    
    # Create test database
    test_db = ApplicationDB("data/test_applications.db")
    
    # Test 1: Check duplicate (should be False)
    print("\n[Test 1] Check duplicate for new URL...")
    test_url = "https://www.stepstone.de/stellenangebote--Test-Job-12345.html"
    is_dup, existing = test_db.check_duplicate(test_url)
    print(f"  Is duplicate: {is_dup}")
    assert not is_dup, "Should not be duplicate"
    print("  ✓ Pass")
    
    # Test 2: Save job
    print("\n[Test 2] Save test job...")
    job_id = test_db.save_processed_job(
        source_url=test_url,
        company_name="Test Company GmbH",
        job_title="Senior Python Developer",
        trello_card_id="abc123",
        trello_card_url="https://trello.com/c/abc123",
        docx_file_path="output/test.docx",
        ai_model="gpt-4o-mini",
        language="de",
        word_count=189,
        generation_cost=0.0002,
        generation_time=2.5,
        cover_letter_text="Sehr geehrte Damen und Herren..."
    )
    print(f"  Saved with job_id: {job_id}")
    print("  ✓ Pass")
    
    # Test 3: Check duplicate (should be True now)
    print("\n[Test 3] Check duplicate for same URL...")
    is_dup, existing = test_db.check_duplicate(test_url)
    print(f"  Is duplicate: {is_dup}")
    print(f"  Existing job: {existing['company_name']} - {existing['job_title']}")
    assert is_dup, "Should be duplicate"
    print("  ✓ Pass")
    
    # Test 4: Get recent jobs
    print("\n[Test 4] Get recent jobs...")
    recent = test_db.get_recent_jobs(limit=5)
    print(f"  Found {len(recent)} recent jobs")
    for job in recent:
        print(f"    - {job['company_name']}: {job['job_title']}")
    print("  ✓ Pass")
    
    # Test 5: Get stats
    print("\n[Test 5] Get statistics...")
    stats = test_db.get_stats()
    print(f"  Total jobs: {stats['total_jobs']}")
    print(f"  Total AI cost: ${stats['total_ai_cost']}")
    print(f"  Top companies: {stats['top_companies']}")
    print("  ✓ Pass")
    
    # Test 6: Get cost stats
    print("\n[Test 6] Get cost statistics...")
    cost_stats = test_db.get_cost_stats(period='all')
    print(f"  Generations: {cost_stats['count']}")
    print(f"  Total cost: ${cost_stats['total_cost']}")
    print(f"  Avg cost: ${cost_stats['avg_cost']}")
    print("  ✓ Pass")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    print(f"\nTest database created at: data/test_applications.db")
    print("You can inspect it with: sqlite3 data/test_applications.db")
