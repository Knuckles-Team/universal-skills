from unittest.mock import MagicMock, patch

import pytest

from firefly_iii_mcp.api import ApiClientBase


@pytest.mark.concept("FF-OS.config.ff")
def test_request_returns_json():
    """API client returns parsed JSON. CONCEPT:FF-OS.config.ff"""
    profile = MagicMock()
    profile.configure_requests_session.side_effect = lambda session: session
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="test-token",
        tls_profile=profile,
    )
    response = MagicMock()
    response.json.return_value = {"ok": True}
    with patch.object(client.session, "request", return_value=response):
        assert client.request("GET", "/health") == {"ok": True}


@pytest.mark.concept("FF-OS.config.ff")
def test_request_rejects_tls_override():
    """Callers cannot bypass the resolved TLS profile. CONCEPT:FF-OS.config.ff"""
    profile = MagicMock()
    profile.configure_requests_session.side_effect = lambda session: session
    client = ApiClientBase(
        base_url="https://service.example.invalid",
        token="test-token",
        tls_profile=profile,
    )

    with pytest.raises(ValueError, match="TLS policy overrides"):
        client.request("GET", "/health", verify=False)


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_cleartext_endpoint():
    """The service boundary requires HTTPS. CONCEPT:FF-OS.config.ff"""
    with pytest.raises(ValueError, match="absolute HTTPS URL"):
        ApiClientBase(base_url="http://service.example.invalid", token="test-token")


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_credentials_or_query_in_endpoint():
    """Endpoint configuration cannot carry hidden authority or parameters."""
    with pytest.raises(ValueError, match="must not contain credentials"):
        ApiClientBase(
            base_url="https://user@service.example.invalid", token="test-token"
        )
    with pytest.raises(ValueError, match="query or fragment"):
        ApiClientBase(
            base_url="https://service.example.invalid?tenant=one", token="test-token"
        )


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_header_control_characters():
    """Bearer credentials cannot inject additional headers."""
    with pytest.raises(ValueError, match="token is invalid"):
        ApiClientBase(
            base_url="https://service.example.invalid",
            token="token\r\ninjected-header: value",
        )


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_empty_endpoint():
    """An empty base URL fails the length bound rather than reaching urlsplit."""
    with pytest.raises(ValueError, match="URL is invalid"):
        ApiClientBase(base_url="", token="test-token")


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_control_characters_in_endpoint():
    """A base URL cannot inject a stray header line via control characters."""
    with pytest.raises(ValueError, match="URL is invalid"):
        ApiClientBase(
            base_url="https://service.example.invalid\r\nHost: evil",
            token="test-token",
        )


@pytest.mark.concept("FF-OS.config.ff")
def test_client_rejects_empty_token():
    """An empty bearer token fails the length bound."""
    with pytest.raises(ValueError, match="token is invalid"):
        ApiClientBase(base_url="https://service.example.invalid", token="")


@pytest.mark.concept("FF-OS.config.ff")
def test_client_tolerates_endpoint_with_existing_api_suffix():
    """A base URL already ending in /api is not doubled."""
    profile = MagicMock()
    profile.configure_requests_session.side_effect = lambda session: session
    client = ApiClientBase(
        base_url="https://service.example.invalid/api",
        token="test-token",
        tls_profile=profile,
    )
    assert client.base_url == "https://service.example.invalid/api"
