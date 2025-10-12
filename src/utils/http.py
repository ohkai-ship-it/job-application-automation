"""HTTP utilities with retry support."""

from __future__ import annotations

from typing import Dict, Any, Optional
import time
import requests

from .logging import get_logger


logger = get_logger(__name__)


def request_with_retries(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    retries: int = 3,
    backoff: float = 0.5,
    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Response:
    """Perform an HTTP request with basic retries on transient errors.

    Raises requests.HTTPError for non-success after retries.
    """
    attempt = 0
    last_exc: Optional[Exception] = None

    while attempt <= retries:
        try:
            resp = requests.request(
                method=method.upper(), url=url, params=params, headers=headers, json=json, data=data, timeout=timeout
            )
            if resp.status_code < 400:
                return resp
            if resp.status_code not in retry_on or attempt == retries:
                logger.error("HTTP %s %s failed with %s: %s", method, url, resp.status_code, resp.text[:300])
                resp.raise_for_status()
            else:
                logger.warning("HTTP %s %s returned %s; retrying (attempt %s/%s)", method, url, resp.status_code, attempt + 1, retries)
        except requests.RequestException as e:
            # If this is an HTTPError with a non-retryable status, don't retry
            if isinstance(e, requests.HTTPError):
                status = getattr(getattr(e, 'response', None), 'status_code', None)
                if status is not None and status not in retry_on:
                    logger.error("HTTP %s %s non-retryable error %s: %s", method, url, status, e)
                    raise
            last_exc = e
            if attempt == retries:
                logger.exception("HTTP %s %s failed after retries: %s", method, url, e)
                raise
            logger.warning("HTTP %s %s exception: %s; retrying (attempt %s/%s)", method, url, e, attempt + 1, retries)

        attempt += 1
        time.sleep(backoff * (2 ** (attempt - 1)))

    # Should not reach here
    if last_exc:
        raise last_exc
    raise requests.HTTPError(f"Request failed: {method} {url}")
