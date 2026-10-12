"""SDK transport and authentication templates for generated connectors."""

AUTH_PY = r'''
"""Resolve credential references only when constructing a vendor client."""

from contextlib import ExitStack

from agent_connector_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .api import ApiClientSystem

_client: ApiClientSystem | None = None
_resources = ExitStack()


def get_client() -> ApiClientSystem:
    """Build one client; delegated auth resolves the verified caller per request."""
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("{upper_name}_BASE_URL", "")
    if not base_url:
        raise ValueError("{upper_name}_BASE_URL is required")
    with ExitStack() as resources:
        tls = resolve_tls_profile("{short_name}")
        resources.callback(tls.cleanup)
        delegation = DelegationSettings.from_settings()
        if delegation.enabled:
            token_tls = resolve_tls_profile("oidc")
            resources.callback(token_tls.cleanup)
            token_client = create_http_client(
                HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
            )
            resources.callback(token_client.close)
            auth = DelegatedTokenAuth(delegation, http_client=token_client)
        else:
            auth = bearer_auth(setting("{upper_name}_TOKEN_REF", ""))
        client = ApiClientSystem(base_url=base_url, auth=auth, tls_profile=tls)
        resources.callback(client.close)
        _resources = resources.pop_all()
        _client = client
    return _client


def close_client() -> None:
    """Release the cached client and any materialized TLS resources."""
    global _client
    try:
        _resources.close()
    finally:
        _client = None
'''

API_CLIENT_BASE = r'''
"""A bounded vendor HTTP client using the connector SDK transport contract."""

import json
import time
from typing import Any
from urllib.parse import SplitResult, urljoin, urlsplit

import httpx
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.profile import ResolvedTLSProfile

from ..error_authority import AGENT_ERROR_ACCEPT

_MAX_RESPONSE_BYTES = 16 * 1024 * 1024
_MAX_RESPONSE_SECONDS = 60.0
_REQUEST_TIMEOUT_S = 30.0


def _origin(parsed: SplitResult) -> tuple[str, str, int]:
    scheme = parsed.scheme.lower()
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, (parsed.hostname or "").lower(), port


def _validate_base_url(base_url: str) -> tuple[str, tuple[str, str, int]]:
    rendered = str(base_url or "").strip()
    if not rendered or len(rendered) > 2048 or any(c in rendered for c in "\x00\r\n"):
        raise ValueError("Invalid service base URL")
    try:
        parsed = urlsplit(rendered)
        origin = _origin(parsed)
    except ValueError as exc:
        raise ValueError("Invalid service base URL") from exc
    if (
        parsed.scheme.lower() not in {{"http", "https"}}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Service base URL must be HTTP(S) without credentials")
    return rendered.rstrip("/") + "/", origin


def _request_url(
    base_url: str, expected_origin: tuple[str, str, int], path: str
) -> str:
    rendered = str(path or "")
    if len(rendered) > 4096 or any(c in rendered for c in "\x00\r\n"):
        raise ValueError("Invalid API path")
    try:
        supplied = urlsplit(rendered)
        if supplied.username is not None or supplied.password is not None:
            raise ValueError("API path must not contain credentials")
        url = urljoin(base_url, rendered)
        if _origin(urlsplit(url)) != expected_origin:
            raise ValueError("API path changed the configured service origin")
    except ValueError as exc:
        raise ValueError("Invalid API path") from exc
    return url


class ApiClientBase:
    """Use SDK auth objects; tokens never travel through default headers."""

    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth,
        tls_profile: ResolvedTLSProfile | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url, self._origin = _validate_base_url(base_url)
        self.session = create_http_client(
            HttpClientOptions(
                base_url=self.base_url,
                timeout=_REQUEST_TIMEOUT_S,
                auth=auth,
                tls=tls_profile,
                headers={{"Accept": AGENT_ERROR_ACCEPT}},
            ),
            transport=transport,
        )

    def close(self) -> None:
        """Close the owned HTTP connection pool."""
        self.session.close()

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Return bounded JSON or a bounded text response from the same origin."""
        url = _request_url(self.base_url, self._origin, path)
        if kwargs.get("follow_redirects") not in (None, False):
            raise ValueError("Redirect following is disabled")
        if "timeout" in kwargs:
            raise ValueError("Request timeout is controlled by the client")
        kwargs["follow_redirects"] = False
        with self.session.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            declared = response.headers.get("content-length")
            if declared:
                try:
                    declared_size = int(declared)
                except ValueError as exc:
                    raise RuntimeError("Invalid response content length") from exc
                if declared_size < 0 or declared_size > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("Response size limit exceeded")
            body = bytearray()
            deadline = time.monotonic() + _MAX_RESPONSE_SECONDS
            for chunk in response.iter_bytes():
                if time.monotonic() > deadline:
                    raise RuntimeError("Response time limit exceeded")
                if len(body) + len(chunk) > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("Response size limit exceeded")
                body.extend(chunk)
        if response.status_code == 204 or not body:
            return {{"status": response.status_code}}
        try:
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {{
                "status": response.status_code,
                "text": body.decode("utf-8", errors="replace")[:4096],
            }}
'''

TESTS_AUTH = r"""
from unittest.mock import MagicMock, patch

import httpx
import pytest
from agent_connector_sdk.auth.delegation import DelegatedTokenAuth
from agent_connector_sdk.credentials.references import SecretReferenceError

import {pkg_dir}.auth as auth_module


@pytest.fixture(autouse=True)
def configured_client(monkeypatch):
    auth_module.close_client()
    monkeypatch.setattr(auth_module, "load_config", lambda: None)
    monkeypatch.setenv("{upper_name}_BASE_URL", "https://service.example.invalid")
    monkeypatch.setenv("{upper_name}_TOKEN_REF", "env://SCAFFOLD_TEST_TOKEN")
    monkeypatch.setenv("SCAFFOLD_TEST_TOKEN", "test-token")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    yield
    auth_module.close_client()


@pytest.mark.concept("{concept_prefix}-001")
def test_client_resolves_reference_and_cleans_up():
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "ApiClientSystem") as client_cls,
    ):
        client = auth_module.get_client()
        assert auth_module.get_client() is client
        kwargs = client_cls.call_args.kwargs
        request = httpx.Request("GET", "https://service.example.invalid")
        authorized = next(kwargs["auth"].auth_flow(request))
        assert authorized.headers["Authorization"] == "Bearer test-token"
        assert "test-token" not in repr(kwargs["auth"])
        assert "token" not in kwargs
        auth_module.close_client()
        client.close.assert_called_once()
        tls.cleanup.assert_called_once()


def test_literal_credential_rejected_and_tls_cleaned(monkeypatch):
    monkeypatch.setenv("{upper_name}_TOKEN_REF", "not-a-reference")
    tls = MagicMock()
    with patch.object(auth_module, "resolve_tls_profile", return_value=tls):
        with pytest.raises(SecretReferenceError):
            auth_module.get_client()
    tls.cleanup.assert_called_once()
    assert auth_module._client is None


def test_failed_client_creation_cleans_tls():
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "ApiClientSystem", side_effect=ValueError("invalid")),
        pytest.raises(ValueError, match="invalid"),
    ):
        auth_module.get_client()
    tls.cleanup.assert_called_once()
    assert auth_module._client is None


def test_delegation_uses_per_request_auth(monkeypatch):
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    monkeypatch.setenv("OIDC_TOKEN_URL", "https://identity.example.invalid/token")
    monkeypatch.setenv("OIDC_CLIENT_ID", "test-client")
    monkeypatch.setenv("OIDC_CLIENT_SECRET_REF", "env://SCAFFOLD_TEST_TOKEN")
    monkeypatch.setenv("AUDIENCE", "test-service")
    token_client = MagicMock()
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "create_http_client", return_value=token_client),
        patch.object(auth_module, "ApiClientSystem") as client_cls,
        patch.object(auth_module, "bearer_auth") as fixed_auth,
    ):
        auth_module.get_client()
        assert isinstance(client_cls.call_args.kwargs["auth"], DelegatedTokenAuth)
        fixed_auth.assert_not_called()
        auth_module.close_client()
        token_client.close.assert_called_once()
"""

TESTS_API_WRAPPER = r"""
import ssl

import httpx
import pytest
from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.tls.errors import TransportSecurityError
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from {pkg_dir}.api import ApiClientBase
from {pkg_dir}.api import api_client_base


@pytest.fixture
def client_factory(monkeypatch):
    monkeypatch.setenv("SCAFFOLD_TEST_TOKEN", "test-token")
    clients = []

    def create(handler, base_url="https://service.example.invalid"):
        client = ApiClientBase(
            base_url=base_url,
            auth=bearer_auth("env://SCAFFOLD_TEST_TOKEN"),
            transport=httpx.MockTransport(handler),
        )
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


@pytest.mark.concept("{concept_prefix}-001")
def test_request_returns_json_and_uses_sdk_auth(client_factory):
    def respond(request):
        assert request.url == httpx.URL("https://service.example.invalid/health")
        assert request.headers["Authorization"] == "Bearer test-token"
        assert all(value == 30.0 for value in request.extensions["timeout"].values())
        return httpx.Response(200, json={{"ok": True}})

    client = client_factory(respond)
    assert client.request("GET", "/health") == {{"ok": True}}
    assert client.session.follow_redirects is False
    assert client.session.trust_env is False


@pytest.mark.parametrize("path", [
    "https://other.example.invalid/health",
    "//other.example.invalid/health",
    "https://user:secret@service.example.invalid/health",
    "https://service.example.invalid:8443/health",
])
def test_request_rejects_origin_or_credentials(client_factory, path):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    with pytest.raises(ValueError, match="API path"):
        client.request("GET", path)
    assert not calls


def test_redirect_not_followed(client_factory):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(302, headers={{"location": "https://other.example.invalid"}})

    client = client_factory(respond)
    with pytest.raises(httpx.HTTPStatusError):
        client.request("GET", "/health")
    assert len(calls) == 1


@pytest.mark.parametrize("options", [{{"follow_redirects": True}}, {{"timeout": None}}])
def test_request_rejects_safety_overrides(client_factory, options):
    client = client_factory(lambda request: httpx.Response(200, json={{}}))
    with pytest.raises(ValueError):
        client.request("GET", "/health", **options)


def test_plaintext_remote_rejected(client_factory):
    with pytest.raises(ValueError, match="plaintext"):
        client_factory(lambda request: httpx.Response(200), "http://service.example.invalid")


def test_tls_cannot_disable_verification():
    with pytest.raises(TransportSecurityError):
        resolve_tls_profile("{short_name}", profile={{"verify": False}})
    profile = resolve_tls_profile("{short_name}", profile={{"trust_env": False}})
    try:
        assert profile.ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert profile.ssl_context.check_hostname
        assert profile.ssl_context.minimum_version >= ssl.TLSVersion.TLSv1_2
    finally:
        profile.cleanup()


def test_oversized_response_rejected(client_factory, monkeypatch):
    monkeypatch.setattr(api_client_base, "_MAX_RESPONSE_BYTES", 8)
    client = client_factory(lambda request: httpx.Response(200, content=b"too large"))
    with pytest.raises(RuntimeError, match="size limit"):
        client.request("GET", "/health")


def test_stream_without_length_still_bounded(client_factory, monkeypatch):
    class Chunks(httpx.SyncByteStream):
        def __iter__(self):
            yield b"first"
            yield b"second"

    monkeypatch.setattr(api_client_base, "_MAX_RESPONSE_BYTES", 8)
    client = client_factory(lambda request: httpx.Response(200, stream=Chunks()))
    with pytest.raises(RuntimeError, match="size limit"):
        client.request("GET", "/health")


def test_response_deadline_enforced(client_factory, monkeypatch):
    class SlowChunk(httpx.SyncByteStream):
        def __iter__(self):
            monkeypatch.setattr(api_client_base.time, "monotonic", lambda: float("inf"))
            yield b"late"

    client = client_factory(lambda request: httpx.Response(200, stream=SlowChunk()))
    with pytest.raises(RuntimeError, match="time limit"):
        client.request("GET", "/health")
"""
