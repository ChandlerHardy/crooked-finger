"""
Sliding-window per-IP rate limiter for AI mutations.

Single-process in-memory store (uvicorn runs one worker on OCI). If we ever
scale to multiple workers/replicas, swap for Redis-backed storage.

Admin users (User.is_admin == True) bypass all limits.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from strawberry.types import Info

logger = logging.getLogger(__name__)

# Per-(ip) timestamps in monotonic seconds. Old entries are pruned on access.
_buckets: Dict[str, Deque[float]] = defaultdict(deque)

# Tunables
CHAT_LIMIT_PER_MINUTE = 10
WINDOW_SECONDS = 60


class RateLimitExceeded(Exception):
    """Raised when an IP has exceeded the rate limit window."""


def _client_ip(info: Info) -> str:
    """Resolve the originating client IP, honoring nginx forwarding headers."""
    request = info.context.get("request")
    if request is None:
        return "unknown"
    headers = request.headers
    # nginx sets X-Forwarded-For with the chain; first entry is the original client.
    fwd = headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real = headers.get("x-real-ip")
    if real:
        return real.strip()
    if request.client:
        return request.client.host
    return "unknown"


def _is_admin(info: Info) -> bool:
    user = info.context.get("user")
    return bool(user and getattr(user, "is_admin", False))


def check_chat_rate_limit(info: Info) -> None:
    """Raise RateLimitExceeded if the client IP is over the limit. Admins bypass."""
    if _is_admin(info):
        return

    ip = _client_ip(info)
    now = time.monotonic()
    cutoff = now - WINDOW_SECONDS

    bucket = _buckets[ip]
    while bucket and bucket[0] < cutoff:
        bucket.popleft()

    if len(bucket) >= CHAT_LIMIT_PER_MINUTE:
        retry_in = int(WINDOW_SECONDS - (now - bucket[0])) + 1
        logger.warning(
            "Rate limit exceeded for ip=%s (window=%ds, limit=%d, retry_in=%ds)",
            ip, WINDOW_SECONDS, CHAT_LIMIT_PER_MINUTE, retry_in,
        )
        raise RateLimitExceeded(
            f"Rate limit exceeded ({CHAT_LIMIT_PER_MINUTE} requests per "
            f"{WINDOW_SECONDS}s). Try again in ~{retry_in}s."
        )

    bucket.append(now)

    # Soft cap on the dict to bound memory under bot floods. 50k unique IPs
    # is well above any realistic legit use; if we hit it, prune empty buckets.
    if len(_buckets) > 50_000:
        empty = [k for k, v in _buckets.items() if not v]
        for k in empty:
            del _buckets[k]
