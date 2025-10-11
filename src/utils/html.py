"""HTML helper utilities used by helper scripts and scraper diagnostics.

This module provides small, composable functions for loading and parsing HTML,
finding common elements, extracting JSON-LD blocks, and performing keyword
searches. Helper scripts (like inspect_html.py) can import these functions to
avoid duplicating logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, List, Tuple, Any

from bs4 import BeautifulSoup


def load_html_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read an HTML file and return its contents as a string.

    Args:
        path: File path to read
        encoding: Text encoding (default utf-8)

    Returns:
        Raw HTML string
    """
    p = Path(path)
    with p.open("r", encoding=encoding) as f:
        return f.read()


def parse_html(html: str, parser: str = "lxml") -> BeautifulSoup:
    """Parse HTML content into a BeautifulSoup object.

    Args:
        html: Raw HTML string
        parser: Parser name for BeautifulSoup (default lxml)

    Returns:
        BeautifulSoup DOM
    """
    return BeautifulSoup(html, parser)


def find_headers(
    soup: BeautifulSoup,
    levels: Iterable[str] = ("h1", "h2", "h3"),
    limit: int | None = None,
) -> List[Tuple[str, str]]:
    """Find header tags and return tuples of (tag_name, text).

    Args:
        soup: Parsed DOM
        levels: Header tag levels to search for
        limit: Optional limit of items to return

    Returns:
        List of (tag_name, text_content)
    """
    headers = soup.find_all(list(levels))
    results: List[Tuple[str, str]] = []
    for header in headers:
        text = header.get_text(strip=True)
        results.append((header.name, text))
        if limit is not None and len(results) >= limit:
            break
    return results


def find_data_at_elements(
    soup: BeautifulSoup, limit: int | None = None
) -> List[Tuple[str, str]]:
    """Find elements with a data-at attribute and return (data_at, text).

    Args:
        soup: Parsed DOM
        limit: Optional limit of items to return

    Returns:
        List of (data-at value, text_content)
    """
    elems = soup.find_all(attrs={"data-at": True})
    results: List[Tuple[str, str]] = []
    for el in elems:
        data_at = el.get("data-at") or ""
        text = el.get_text(strip=True)
        results.append((data_at, text))
        if limit is not None and len(results) >= limit:
            break
    return results


def extract_json_ld_blocks(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract and parse all JSON-LD script blocks.

    Attempts to parse each script[type="application/ld+json"] block. If the
    parsed JSON is a list, each item is yielded. Only objects (dict) are
    returned; non-dict items are ignored.

    Returns:
        List of JSON-LD objects
    """
    import json

    results: List[Dict[str, Any]] = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        content = script.string or ""
        if not content.strip():
            continue
        try:
            data = json.loads(content)
        except Exception:
            # Some sites include invalid JSON (e.g., unescaped). Skip gracefully.
            continue

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    results.append(item)
        elif isinstance(data, dict):
            results.append(data)
    return results


def search_text_occurrences(
    soup: BeautifulSoup, search_term: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """Search for a term in text nodes, returning lightweight context objects.

    Args:
        soup: Parsed DOM
        search_term: Plain substring to look for (case-sensitive as provided)
        limit: Max number of occurrences to return

    Returns:
        List of dicts: {parent_tag, classes, preview}
    """
    matches = soup.find_all(string=lambda t: t and search_term in t)
    results: List[Dict[str, Any]] = []
    for node in matches[:limit]:
        parent = getattr(node, "parent", None)
        parent_tag = getattr(parent, "name", None) or ""
        classes = []
        try:
            classes = parent.get("class") or []
        except Exception:
            classes = []
        text = str(node).strip().replace("\n", " ")
        preview = text[:60] + ("..." if len(text) > 60 else "")
        results.append({
            "parent_tag": parent_tag,
            "classes": classes,
            "preview": preview,
        })
    return results


def search_keywords(
    soup: BeautifulSoup, keywords: Dict[str, str], limit_per: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """Search multiple keywords and return occurrences per key.

    Args:
        soup: Parsed DOM
        keywords: Mapping of logical key -> search term
        limit_per: Max occurrences per keyword

    Returns:
        Dict mapping key -> list of occurrence dicts
    """
    return {
        key: search_text_occurrences(soup, term, limit=limit_per)
        for key, term in keywords.items()
    }
