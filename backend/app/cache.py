"""
cache.py – disk-backed cache keyed by a hash of (model, inputs).

Every Gnani API call MUST go through the cache wrapper so that identical
inputs are never billed twice.  Uses diskcache for persistence across runs.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import diskcache

from .config import settings

logger = logging.getLogger(__name__)

# ── Module-level cache instance ───────────────────────────────────────────────
_cache: Optional[diskcache.Cache] = None


def _get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        _cache = diskcache.Cache(str(settings.cache_dir))
    return _cache


# ── Key construction ──────────────────────────────────────────────────────────

def make_cache_key(_model_name: str, **kwargs: Any) -> str:
    """
    Deterministically hash (model, kwargs) into a cache key.

    Binary values (bytes) are hashed via SHA-256 before JSON serialisation so
    the key stays a compact, printable string.
    """
    serialisable: dict[str, Any] = {"_model": _model_name}
    for k, v in sorted(kwargs.items()):
        if isinstance(v, bytes):
            serialisable[k] = hashlib.sha256(v).hexdigest()
        else:
            serialisable[k] = v
    raw = json.dumps(serialisable, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


# ── Public helpers ────────────────────────────────────────────────────────────

def get_cached(key: str) -> Optional[Any]:
    """Return cached value or None."""
    cache = _get_cache()
    value = cache.get(key)
    if value is not None:
        logger.debug("Cache HIT  key=%s", key[:16])
    return value


def set_cached(key: str, value: Any, expire: Optional[int] = None) -> None:
    """Store value in cache, optionally with TTL in seconds."""
    cache = _get_cache()
    cache.set(key, value, expire=expire)
    logger.debug("Cache WRITE key=%s", key[:16])


def cached_call(
    model: str,
    fn: Callable[[], Any],
    **key_kwargs: Any,
) -> Any:
    """
    Generic caching wrapper.

    Usage::

        result = cached_call(
            model="prisma-v2.5",
            fn=lambda: gnani_client.transcribe(audio_bytes, lang="hi-IN"),
            audio_hash=sha256(audio_bytes),
            lang="hi-IN",
        )

    If the key is already in cache the function is not called.
    """
    key = make_cache_key(model, **key_kwargs)
    cached = get_cached(key)
    if cached is not None:
        return cached
    result = fn()
    set_cached(key, result)
    return result


def cache_stats() -> dict[str, int]:
    """Return number of cached entries."""
    cache = _get_cache()
    return {"entries": len(cache)}
