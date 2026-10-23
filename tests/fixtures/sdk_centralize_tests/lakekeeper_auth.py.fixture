"""Identity credentials loader for the Lakekeeper (Iceberg REST catalog) client.

Lakekeeper is OIDC-authenticated via Keycloak (realm ``homelab``) using the
OAuth2 client-credentials grant. **The landmine**, named explicitly in
``services/lakekeeper/AGENTS.md``: the shared Iceberg-REST/OAuth2 client
convention many SDKs default to is ``scope=catalog`` — Lakekeeper's own
Keycloak client (``lakekeeper-service``) is provisioned for
``scope=lakekeeper``, and the default silently gets a token Lakekeeper
rejects. Every token minted here passes ``scope=lakekeeper`` explicitly,
never the ambient default.

Tokens are short-lived (observed ``expires_in=300`` against the live
deployment) — this module mints once, caches, and refreshes with a skew
margin rather than re-minting on every call or baking a token in at client
construction time (a client built once at process start must not go stale
mid-lifetime).
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import requests
from agent_connector_sdk.config import setting
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from lakekeeper_mcp.api.api_client_base import LakekeeperApiError
from lakekeeper_mcp.api_client import Api

logger = logging.getLogger(__name__)

# Refresh this many seconds before the token's declared expiry.
_EXPIRY_SKEW_S = 15.0
# Assumed lifetime before the first mint reveals the IdP's real expires_in.
_DEFAULT_TOKEN_TTL_S = 60.0

# Explicit, never the shared-client default ("catalog") — see module docstring.
LAKEKEEPER_OAUTH_SCOPE = "lakekeeper"


class _TokenCache:
    """Thread-safe, single-credential client-credentials token cache."""

    def __init__(
        self,
        *,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str = LAKEKEEPER_OAUTH_SCOPE,
        verify: Any = True,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._verify = verify
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at: float = 0.0

    def get(self) -> str:
        with self._lock:
            now = time.monotonic()
            if self._token and now < self._expires_at - _EXPIRY_SKEW_S:
                return self._token
            self._mint(now)
            assert self._token is not None
            return self._token

    def _mint(self, now: float) -> None:
        try:
            response = requests.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "scope": self._scope,
                },
                timeout=15.0,
                verify=self._verify,
            )
        except requests.RequestException as exc:
            raise LakekeeperApiError(
                f"Lakekeeper OAuth2 token mint failed (network): {exc}"
            ) from exc

        if response.status_code >= 400:
            raise LakekeeperApiError(
                f"Lakekeeper OAuth2 token mint failed: HTTP {response.status_code}",
                status_code=response.status_code,
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise LakekeeperApiError(
                "Lakekeeper OAuth2 token endpoint returned a non-JSON body"
            ) from exc

        token = payload.get("access_token")
        if not token:
            raise LakekeeperApiError(
                "Lakekeeper OAuth2 token response carried no access_token"
            )
        granted_scope = str(payload.get("scope", ""))
        if self._scope not in granted_scope.split():
            # Fail closed rather than silently proceed with a token whose
            # granted scope diverges from what was requested — the exact
            # `scope=catalog` landmine this module exists to avoid.
            raise LakekeeperApiError(
                f"Lakekeeper OAuth2 token was granted scope={granted_scope!r}, "
                f"expected {self._scope!r} to be included"
            )
        ttl = float(
            payload.get("expires_in", _DEFAULT_TOKEN_TTL_S) or _DEFAULT_TOKEN_TTL_S
        )
        self._token = token
        self._expires_at = now + ttl


_cache_lock = threading.Lock()
_cache: _TokenCache | None = None


def _token_cache() -> _TokenCache:
    global _cache
    with _cache_lock:
        if _cache is not None:
            return _cache
        token_url = setting("LAKEKEEPER_OAUTH_TOKEN_URL", "") or (
            setting("LAKEKEEPER_KEYCLOAK_URL", "http://localhost:8080").rstrip("/")
            + f"/realms/{setting('LAKEKEEPER_KEYCLOAK_REALM', 'homelab')}"
            + "/protocol/openid-connect/token"
        )
        client_id = setting("LAKEKEEPER_SERVICE_CLIENT_ID", "lakekeeper-service")
        client_secret = setting("LAKEKEEPER_SERVICE_CLIENT_SECRET", "")
        if not client_secret:
            raise LakekeeperApiError(
                "LAKEKEEPER_SERVICE_CLIENT_SECRET is not configured — cannot mint a "
                "Lakekeeper OAuth2 token"
            )
        tls_profile = resolve_tls_profile(
            "lakekeeper",
            profile_name=setting("LAKEKEEPER_TLS_PROFILE", None),
            profile_ref=setting("LAKEKEEPER_TLS_PROFILE_REF", None),
        )
        verify = tls_profile.requests_kwargs().get("verify", True)
        _cache = _TokenCache(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            scope=setting("LAKEKEEPER_OAUTH_SCOPE", LAKEKEEPER_OAUTH_SCOPE),
            verify=verify,
        )
        return _cache


def get_token() -> str:
    """Return a cached, valid Lakekeeper OAuth2 access token, minting/refreshing as needed."""
    return _token_cache().get()


def get_client() -> Api:
    """Build an authenticated Lakekeeper API client from the environment.

    Honors ``LAKEKEEPER_URL`` for the bare origin (never including
    ``/catalog`` — the client appends both ``/catalog/v1`` and
    ``/management/v1`` roots itself), ``LAKEKEEPER_WAREHOUSE`` as the default
    warehouse name, and the Keycloak client-credentials variables above for
    the bearer token — minted fresh per client via :func:`get_token`, never a
    static baked-in ``LAKEKEEPER_TOKEN``.
    """
    base_url = setting("LAKEKEEPER_URL", "http://localhost:8181")
    default_warehouse = setting("LAKEKEEPER_WAREHOUSE", "")
    tls_profile = resolve_tls_profile(
        "lakekeeper",
        profile_name=setting("LAKEKEEPER_TLS_PROFILE", None),
        profile_ref=setting("LAKEKEEPER_TLS_PROFILE_REF", None),
    )
    return Api(
        base_url=base_url,
        token_provider=get_token,
        tls_profile=tls_profile,
        default_warehouse=default_warehouse,
    )
