"""
Web search functionality using DuckDuckGo API.

This module provides a clean abstraction layer for web search operations,
specifically designed to find job-related information such as career pages,
contact persons, and company addresses.
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass

from duckduckgo_search import DDGS

# Use custom logger from utils
try:
    from .log_config import get_logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.log_config import get_logger

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Structured search result."""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0


class WebSearcher:
    """
    Web search abstraction using DuckDuckGo.
    
    Features:
    - No API key required
    - Privacy-friendly
    - Rate limiting built-in
    - Site-specific search capabilities
    """
    
    def __init__(
        self,
        rate_limit_delay: float = 1.0,
        max_results: int = 10,
        region: str = "de-de"
    ):
        """
        Initialize the WebSearcher.
        
        Args:
            rate_limit_delay: Seconds to wait between searches (politeness)
            max_results: Maximum number of results to return per search
            region: Search region (de-de for Germany, en-us for US)
        """
        self.rate_limit_delay = rate_limit_delay
        self.max_results = max_results
        self.region = region
        self._last_search_time = 0.0
        
        logger.info(
            f"WebSearcher initialized | region={region} | max_results={max_results} | delay={rate_limit_delay}s"
        )
    
    def _rate_limit(self):
        """Enforce rate limiting between searches."""
        elapsed = time.time() - self._last_search_time
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self._last_search_time = time.time()
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Perform a general web search.
        
        Args:
            query: The search query string
            max_results: Override default max_results for this search
            
        Returns:
            List of SearchResult objects
            
        Example:
            >>> searcher = WebSearcher()
            >>> results = searcher.search("Python programming tutorials")
            >>> for r in results:
            ...     print(f"{r.title}: {r.url}")
        """
        self._rate_limit()
        
        max_results = max_results or self.max_results
        
        logger.info(f"Web search | query='{query}' | max_results={max_results}")
        
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(
                    query,
                    region=self.region,
                    safesearch="moderate",
                    max_results=max_results
                ))
            
            results = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")
                )
                for r in raw_results
            ]
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_site(
        self,
        query: str,
        site: str,
        max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search within a specific website/domain.
        
        Args:
            query: The search query string
            site: The domain to search within (e.g., "example.com")
            max_results: Override default max_results for this search
            
        Returns:
            List of SearchResult objects
            
        Example:
            >>> searcher = WebSearcher()
            >>> results = searcher.search_site(
            ...     query="software engineer",
            ...     site="careers.google.com"
            ... )
        """
        # Build site-specific query using Google-style "site:" operator
        site_query = f"{query} site:{site}"
        
        logger.info(f"Site search | query='{query}' | site={site}")
        
        return self.search(site_query, max_results=max_results)
    
    def search_exact_phrase(
        self,
        phrase: str,
        additional_terms: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search for an exact phrase.
        
        Args:
            phrase: The exact phrase to search for
            additional_terms: Optional additional search terms (not exact)
            max_results: Override default max_results for this search
            
        Returns:
            List of SearchResult objects
            
        Example:
            >>> searcher = WebSearcher()
            >>> results = searcher.search_exact_phrase(
            ...     phrase="Head of Recruiting",
            ...     additional_terms="Acme Corporation"
            ... )
        """
        # Quote the phrase for exact match
        query = f'"{phrase}"'
        if additional_terms:
            query = f"{query} {additional_terms}"
        
        logger.info(f"Exact phrase search | phrase='{phrase}' | additional='{additional_terms}'")
        
        return self.search(query, max_results=max_results)
    
    def find_company_pages(
        self,
        company_name: str,
        keywords: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Find web pages related to a company.
        
        Args:
            company_name: Name of the company
            keywords: Additional keywords to narrow search (e.g., ["careers", "jobs"])
            
        Returns:
            List of SearchResult objects, prioritizing official company pages
            
        Example:
            >>> searcher = WebSearcher()
            >>> results = searcher.find_company_pages(
            ...     company_name="Acme Corporation",
            ...     keywords=["careers", "jobs"]
            ... )
        """
        # Build query with company name and keywords
        query_parts = [company_name]
        if keywords:
            query_parts.extend(keywords)
        query = " ".join(query_parts)
        
        logger.info(f"Finding company pages | company='{company_name}' | keywords={keywords}")
        
        results = self.search(query)
        
        # Score results based on relevance to company
        company_lower = company_name.lower()
        for result in results:
            score = 0.0
            
            # High score if company name in domain
            if company_lower.replace(" ", "") in result.url.lower():
                score += 5.0
            
            # Medium score if company name in title
            if company_lower in result.title.lower():
                score += 3.0
            
            # Low score if company name in snippet
            if company_lower in result.snippet.lower():
                score += 1.0
            
            # Bonus for keywords in URL
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in result.url.lower():
                        score += 2.0
            
            result.relevance_score = score
        
        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        logger.info(f"Scored and sorted {len(results)} results")
        return results


# Convenience function for quick searches
def quick_search(query: str, max_results: int = 5) -> List[SearchResult]:
    """
    Quick search utility for one-off searches.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of SearchResult objects
    """
    searcher = WebSearcher(max_results=max_results)
    return searcher.search(query)


# Module-level test
if __name__ == "__main__":
    import sys
    import os
    # Add parent directory to path so imports work when running directly
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    
    from utils.log_config import get_logger
    
    # Configure logging for test
    import logging as stdlib_logging
    stdlib_logging.basicConfig(
        level=stdlib_logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    print("=" * 80)
    print("WEB SEARCH MODULE TEST")
    print("=" * 80)
    
    searcher = WebSearcher(max_results=3)
    
    # Test 1: General search
    print("\n1. General Search Test")
    print("-" * 80)
    results = searcher.search("Python web scraping")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Snippet: {result.snippet[:100]}...")
    
    # Test 2: Site-specific search
    print("\n\n2. Site-Specific Search Test")
    print("-" * 80)
    results = searcher.search_site(
        query="software engineer",
        site="stackoverflow.com"
    )
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
    
    # Test 3: Company page search
    print("\n\n3. Company Page Search Test")
    print("-" * 80)
    results = searcher.find_company_pages(
        company_name="Google",
        keywords=["careers", "jobs"]
    )
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title} (score: {result.relevance_score})")
        print(f"   URL: {result.url}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
