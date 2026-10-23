import inspect
from unittest.mock import MagicMock, patch

import pytest
import requests

from audiobookshelf_mcp.api import ApiClientBase, ApiClientSystem


def _profile() -> MagicMock:
    profile = MagicMock()
    profile.configure_requests_session.side_effect = lambda session: session
    return profile


def _response(
    status: int = 200,
    body: bytes = b"{}",
    content_type: str = "application/json",
) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status
    response.headers = {"Content-Type": content_type}
    response.iter_content.return_value = [body]
    return response


@pytest.mark.concept("AS-OS.identity.abs")
def test_request_returns_json_and_disables_redirects():
    """The current client returns JSON through a fixed verified request shape."""
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=_profile(),
    )
    with patch.object(
        client.session, "request", return_value=_response(200, b'{"ok":true}')
    ) as request:
        assert client.request("GET", "/api/libraries") == {"ok": True}
    assert request.call_args.kwargs["timeout"] == 60.0
    assert request.call_args.kwargs["allow_redirects"] is False
    assert request.call_args.kwargs["stream"] is True
    assert "verify" not in request.call_args.kwargs
    assert "proxies" not in request.call_args.kwargs


@pytest.mark.concept("AS-OS.identity.abs")
def test_dynamic_path_parameter_is_encoded():
    """Opaque provider identifiers cannot escape their path segment."""
    client = ApiClientSystem(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=_profile(),
    )
    with patch.object(client.session, "request", return_value=_response()) as request:
        client.get_author_by_id("author/segment")
    assert request.call_args.args[1].endswith("/api/authors/author%2Fsegment")


@pytest.mark.concept("AS-OS.identity.abs")
@pytest.mark.parametrize(
    "base_url, message",
    [
        ("http://service.example.invalid", "absolute HTTPS"),
        ("https://user@service.example.invalid", "must not contain credentials"),
        ("https://service.example.invalid?tenant=one", "query or fragment"),
    ],
)
def test_client_rejects_unsafe_authorities(base_url: str, message: str):
    """Endpoint configuration cannot weaken or obscure the target authority."""
    with pytest.raises(Exception, match=message):
        ApiClientBase(base_url=base_url, token="runtime-token")


@pytest.mark.concept("AS-OS.identity.abs")
@pytest.mark.parametrize(
    "token",
    ["token\r\ninjected: value", "token with spaces", "env://UNRESOLVED_TOKEN"],
)
def test_client_rejects_unresolved_or_injectable_credentials(token: str):
    """Bearer credentials must be resolved and safe for one header value."""
    with pytest.raises(Exception, match="resolved runtime credential"):
        ApiClientBase(base_url="https://service.example.invalid", token=token)


@pytest.mark.concept("AS-OS.identity.abs")
def test_request_has_no_per_call_transport_override_surface():
    """Callers cannot override TLS, proxy, redirect, or timeout policy."""
    parameters = inspect.signature(ApiClientBase.request).parameters
    assert "kwargs" not in parameters
    assert {"verify", "cert", "proxies", "timeout"}.isdisjoint(parameters)


@pytest.mark.concept("AS-OS.identity.abs")
def test_provider_error_body_is_not_exposed():
    """HTTP failures return a stable status class without provider content."""
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=_profile(),
    )
    response = _response(500, b'{"detail":"sensitive provider content"}')
    with patch.object(client.session, "request", return_value=response):
        with pytest.raises(Exception) as exc_info:
            client.request("GET", "/api/libraries")
    assert "sensitive provider content" not in str(exc_info.value)


@pytest.mark.concept("AS-OS.identity.abs")
def test_declared_oversized_response_is_rejected_before_body_read():
    """A provider cannot force unbounded buffering before the response cap."""
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=_profile(),
    )
    response = _response()
    response.headers["Content-Length"] = str(64 * 1024 * 1024 + 1)
    with patch.object(client.session, "request", return_value=response):
        with pytest.raises(Exception, match="exceeded the connector limit"):
            client.request("GET", "/api/libraries")
    response.close.assert_called_once()


@pytest.mark.concept("AS-OS.identity.abs")
def test_retry_after_nonfinite_value_uses_bounded_backoff():
    """Malformed retry metadata cannot create an invalid or unbounded sleep."""
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=_profile(),
        max_retries=1,
    )
    retry = _response(429)
    retry.headers["Retry-After"] = "nan"
    success = _response()
    with patch.object(client.session, "request", side_effect=[retry, success]):
        with patch("audiobookshelf_mcp.api.api_client_base.time.sleep") as sleep:
            assert client.request("GET", "/api/libraries") == {}
    sleep.assert_called_once_with(1.0)
    retry.close.assert_called_once()
    success.close.assert_called_once()


@pytest.mark.concept("AS-OS.identity.abs")
def test_close_removes_in_memory_authorization_header():
    """Closing the client removes its bearer header and TLS material."""
    profile = _profile()
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="runtime-token",
        tls_profile=profile,
    )
    client.close()
    assert "Authorization" not in client.session.headers
    profile.cleanup.assert_called_once()
