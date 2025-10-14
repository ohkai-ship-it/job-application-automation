"""Centralized error reporting utilities.

Writes structured error events to JSON files under OUTPUT_DIR/errors and logs
them via the project logger. Designed to be side-effect-free beyond local I/O
unless explicitly configured for external sinks in the future.
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, Optional

from .log_config import get_logger


logger = get_logger(__name__)

SENSITIVE_KEYS = {
    "password",
    "token",
    "apikey",
    "api_key",
    "api-token",
    "secret",
    "authorization",
    "auth",
    "key",
}


def _output_dir() -> Path:
    base = os.getenv("OUTPUT_DIR", "output")
    return Path(base) / "errors"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _sanitize(obj: Any, parent_key: str = "") -> Any:
    """Recursively sanitize dictionaries by masking sensitive values.

    - Masks values when key name contains any of SENSITIVE_KEYS substrings (case-insensitive).
    - Limits string length to avoid gigantic payloads in error files.
    """
    try:
        if isinstance(obj, dict):
            out: Dict[str, Any] = {}
            for k, v in obj.items():
                k_lower = str(k).lower()
                if any(s in k_lower for s in SENSITIVE_KEYS):
                    out[k] = "***"
                else:
                    out[k] = _sanitize(v, k_lower)
            return out
        if isinstance(obj, (list, tuple)):
            return [
                _sanitize(v, parent_key) for v in (list(obj) if isinstance(obj, tuple) else obj)
            ]
        if isinstance(obj, str):
            return obj if len(obj) <= 2000 else obj[:2000] + "…"
        return obj
    except Exception:  # best-effort sanitize
        return "<sanitize-error>"


def report_error(
    message: str,
    *,
    exc: Optional[BaseException] = None,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "error",
) -> Path:
    """Record an error event to disk and log a concise line.

    Returns the path to the written error JSON file.
    """
    errors_dir = _output_dir()
    _ensure_dir(errors_dir)

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    event_id = f"evt_{ts}"
    stack = None
    exc_type = None
    if exc is not None:
        exc_type = type(exc).__name__
        stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    event = {
        "id": event_id,
        "timestamp": ts,
        "severity": severity,
        "message": message,
        "exception_type": exc_type,
        "stack": stack[:20000] + "…" if isinstance(stack, str) and len(stack) > 20000 else stack,
        "context": _sanitize(context or {}),
        "pid": os.getpid(),
    }

    filename = errors_dir / f"error_{ts}.json"
    try:
        with filename.open("w", encoding="utf-8") as f:
            json.dump(event, f, ensure_ascii=False, indent=2)
    except Exception as write_err:
        # Fall back to logging only if writing fails
        logger.error("Failed to write error report: %s", write_err)
    finally:
        # Always emit a concise log line for observability
        log_fn = logger.error if severity == "error" else logger.warning if severity == "warning" else logger.info
        log_fn("Error event recorded [%s]: %s", event_id, message)

    return filename


__all__ = ["report_error"]
