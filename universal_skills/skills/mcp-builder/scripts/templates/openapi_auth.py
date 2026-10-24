"""Resolve provider credentials and delegated caller auth through canonical SDK APIs."""

from contextlib import ExitStack

import httpx
from agent_connector_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from agent_connector_sdk.auth.static import api_key_auth, bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .api import ApiClientSystem
from .openapi_auth_scheme import AuthKind, declared_scheme
from .openapi_runtime import CONTRACT

_client = None
_resources = ExitStack()


def _bearer_scheme(definition):
    return definition is not None and definition.kind is AuthKind.BEARER


def _delegated_auth(delegation, resources):
    token_tls = resolve_tls_profile("oidc")
    resources.callback(token_tls.cleanup)
    token_client = create_http_client(
        HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
    )
    resources.callback(token_client.close)
    return DelegatedTokenAuth(delegation, http_client=token_client)


def _static_auth(reference, definition):
    if definition is None:
        raise ValueError("A credential requires a declared authentication scheme")
    if definition.kind is AuthKind.HEADER:
        return api_key_auth(reference, header=definition.header)
    return bearer_auth(reference)


def _resolve_auth(resources):
    scheme = setting("__PACKAGE_ENV___AUTH_SCHEME", "__DEFAULT_AUTH_SCHEME__")
    definition = declared_scheme(scheme, CONTRACT["security_schemes"])
    delegation = DelegationSettings.from_settings()
    if delegation.enabled:
        if not _bearer_scheme(definition):
            raise ValueError("Delegation requires a declared HTTP bearer auth scheme")
        return _delegated_auth(delegation, resources), scheme
    reference = setting("__PACKAGE_ENV___TOKEN_REF", "")
    if not reference:
        return httpx.Auth(), None
    return _static_auth(reference, definition), scheme


def get_client():
    """Build one client; delegated auth resolves the verified caller per request."""
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("__PACKAGE_ENV___BASE_URL", "")
    if not base_url:
        raise ValueError("Provider base URL is required")
    with ExitStack() as resources:
        tls = resolve_tls_profile("__SERVICE__")
        resources.callback(tls.cleanup)
        auth, credential_scheme = _resolve_auth(resources)
        client = ApiClientSystem(
            base_url=base_url,
            auth=auth,
            tls_profile=tls,
            credential_scheme=credential_scheme,
            write_mode=(
                "read-write"
                if setting("__PACKAGE_ENV___ALLOW_WRITES", False)
                else "read-only"
            ),
            allow_plaintext=setting("__PACKAGE_ENV___ALLOW_PLAINTEXT", False),
        )
        resources.callback(client.close)
        _resources = resources.pop_all()
        _client = client
    return client


def close_client():
    """Close the cached client, token client and materialized TLS resources."""
    global _client
    try:
        _resources.close()
    finally:
        _client = None
