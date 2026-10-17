"""Shared bounded HTTP boundary for the web-search skill.

TLS, CA bundles, proxies, private-host allowlists, redirects, and response limits
come from the agent-connector-sdk settings and governed HTTP client.  Individual
provider scripts must not add their own ``verify=False`` switches.
"""

from __future__ import annotations

import json
from typing import Any

from urllib.parse import urlencode, urlparse

from agent_connector_sdk.auth.static import ApiKeyAuth
from agent_connector_sdk.config import csv_values, setting
from agent_connector_sdk.http.bodies import read_bounded
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.http.redaction import is_sensitive_name
from agent_connector_sdk.tls.resolve import resolve_tls_profile

_SEARCH_RESPONSE_LIMIT = 4 * 1024 * 1024


def fetch_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch and decode one bounded JSON object through DNS-pinned egress.

    Redirects are not followed: a provider that redirects fails closed.
    """

    private_hosts = tuple(
        sorted(
            host.strip().lower().rstrip(".")
            for host in csv_values(setting("SOURCE_HTTP_ALLOWED_PRIVATE_HOSTS", ""))
            if host
        )
    )
    max_bytes = min(
        int(setting("SOURCE_HTTP_MAX_RESPONSE_BYTES", _SEARCH_RESPONSE_LIMIT)),
        _SEARCH_RESPONSE_LIMIT,
    )
    target = f"{url}?{urlencode(params)}" if params else url
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    plain = {k: v for k, v in (headers or {}).items() if not is_sensitive_name(k)}
    secret = [(k, v) for k, v in (headers or {}).items() if is_sensitive_name(k)]
    auth = ApiKeyAuth(secret[0][1], header=secret[0][0]) if secret else None
    tls = resolve_tls_profile("source-http")
    try:
        options = HttpClientOptions(
            base_url=url,
            timeout=30.0,
            tls=tls,
            headers=plain,
            auth=auth,
            allow_plaintext=host in private_hosts,
            pin_egress=True,
            allowed_private_hosts=private_hosts,
        )
        with create_http_client(options) as client:
            with client.stream("GET", target) as response:
                response.raise_for_status()
                body = read_bounded(response, max_bytes)
                encoding = response.charset_encoding
    finally:
        tls.cleanup()
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
