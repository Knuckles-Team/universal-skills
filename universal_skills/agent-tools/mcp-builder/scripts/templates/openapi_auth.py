"""Construct a provider client using SDK credential references and TLS policy."""

from contextlib import ExitStack

import httpx
from agent_connector_sdk.auth.static import api_key_auth, bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .openapi_runtime import CONTRACT, OpenApiClient

_client = None
_resources = ExitStack()


def get_client():
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("__PACKAGE_ENV___BASE_URL", "")
    if not base_url:
        raise ValueError("Provider base URL is required")
    reference = setting("__PACKAGE_ENV___TOKEN_REF", "")
    scheme = setting("__PACKAGE_ENV___AUTH_SCHEME", "__DEFAULT_AUTH_SCHEME__")
    definition = CONTRACT["security_schemes"].get(scheme, {})
    auth = httpx.Auth()
    if reference:
        if definition.get("type") == "apiKey" and definition.get("in") == "header":
            auth = api_key_auth(reference, header=definition["name"])
        elif (
            definition.get("type") == "http"
            and definition.get("scheme", "").lower() == "bearer"
        ):
            auth = bearer_auth(reference)
        else:
            raise ValueError("Unsupported provider authentication scheme")
    with ExitStack() as resources:
        tls = resolve_tls_profile("__SERVICE__")
        resources.callback(tls.cleanup)
        client = OpenApiClient(
            base_url=base_url,
            auth=auth,
            tls_profile=tls,
            credential_scheme=scheme if reference else None,
            allow_writes=setting("__PACKAGE_ENV___ALLOW_WRITES", False),
        )
        resources.callback(client.close)
        _resources = resources.pop_all()
        _client = client
    return client


def close_client():
    global _client
    try:
        _resources.close()
    finally:
        _client = None
