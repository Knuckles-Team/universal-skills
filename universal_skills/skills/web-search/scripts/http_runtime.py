"""Shared bounded HTTP boundary for the web-search skill.

TLS, CA bundles, proxies, private-host allowlists, redirects, and response limits
come from ``AgentConfig`` and the central source connector policy.  Individual
provider scripts must not add their own ``verify=False`` switches.
"""

from __future__ import annotations

import json
from typing import Any

from scion_sdk.source_connectors.http_safety import (
    configured_source_http_policy,
    safe_get_bytes,
)

_SEARCH_RESPONSE_LIMIT = 4 * 1024 * 1024


def fetch_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch and decode one bounded JSON object through the shared egress policy."""

    policy = configured_source_http_policy()
    body, encoding = safe_get_bytes(
        url,
        params=params,
        headers=headers,
        timeout=30.0,
        max_bytes=min(policy["max_bytes"], _SEARCH_RESPONSE_LIMIT),
        max_redirects=policy["max_redirects"],
        allowed_private_hosts=policy["allowed_private_hosts"],
        allowed_redirect_hosts=policy["allowed_redirect_hosts"],
    )
    decoded = json.loads(body.decode(encoding or "utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("Search provider returned an invalid JSON shape")
    return decoded


def validate_search_request(query: str, max_results: int) -> tuple[str, int]:
    """Bound provider-neutral user input before it reaches any network client."""

    rendered = str(query or "").strip()
    if not rendered or len(rendered.encode("utf-8")) > 2_048 or "\x00" in rendered:
        raise ValueError("Search query is empty or exceeds the size limit")
    count = int(max_results)
    if not 1 <= count <= 50:
        raise ValueError("max_results must be between 1 and 50")
    return rendered, count
