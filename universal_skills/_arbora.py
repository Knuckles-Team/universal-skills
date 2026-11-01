"""Best-effort client for the arbora REST twins of the graph intent tools.

Skill scripts read the knowledge graph through the served arbora surface and
never import an engine or backend package. ``ARBORA_URL`` selects the gateway
and ``ARBORA_TOKEN`` supplies an optional bearer token. Every call returns
``None`` instead of raising, so a skill falls back to its local path when no
gateway is configured.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request

from universal_skills._security.http import SafeHttpError, UrlPolicy, open_json

_MAX_BYTES = 8 * 1024 * 1024


def _post(
    path: str, body: dict[str, Any], *, endpoint: str | None, timeout: float
) -> Any | None:
    base = (endpoint or os.environ.get("ARBORA_URL", "")).rstrip("/")
    if not base:
        return None
    host = (urlsplit(base).hostname or "").lower().rstrip(".")
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("ARBORA_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        base + path,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    policy = UrlPolicy(
        frozenset({host}),
        allow_private_hosts=frozenset({host}),
        allow_http_loopback=True,
    )
    try:
        payload, _ = open_json(
            request, policy=policy, timeout=timeout, max_bytes=_MAX_BYTES
        )
    except (SafeHttpError, ValueError):
        return None
    if isinstance(payload, dict) and payload.get("status") not in (None, "success"):
        return None
    return payload.get("result", payload) if isinstance(payload, dict) else payload


def _rows(result: Any) -> list[dict[str, Any]] | None:
    if isinstance(result, dict):
        for key in ("rows", "results", "data", "items"):
            if isinstance(result.get(key), list):
                result = result[key]
                break
    if not isinstance(result, list):
        return None
    return [row for row in result if isinstance(row, dict)]


def graph_query(
    cypher: str, *, endpoint: str | None = None, timeout: float = 30.0
) -> list[dict[str, Any]] | None:
    """Run one read-only Cypher query through ``POST /api/graph/query``."""
    return _rows(
        _post(
            "/api/graph/query",
            {"query": cypher, "scope": "local"},
            endpoint=endpoint,
            timeout=timeout,
        )
    )


def graph_search(
    query: str, *, top_k: int = 10, endpoint: str | None = None, timeout: float = 30.0
) -> list[dict[str, Any]] | None:
    """Run one hybrid search through ``POST /api/graph/search``."""
    return _rows(
        _post(
            "/api/graph/search",
            {"query": query, "mode": "hybrid", "top_k": top_k},
            endpoint=endpoint,
            timeout=timeout,
        )
    )
