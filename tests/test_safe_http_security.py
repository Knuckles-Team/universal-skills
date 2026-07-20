"""Adversarial coverage for the shared standalone-skill HTTP boundary."""

from __future__ import annotations

import urllib.request

import pytest
from universal_skills._security import http


def test_policy_rejects_wildcards_and_empty_hosts():
    with pytest.raises(ValueError, match="policy"):
        http.UrlPolicy(frozenset())
    with pytest.raises(ValueError, match="policy"):
        http.UrlPolicy(frozenset({"*.example.com"}))


def test_url_rejects_embedded_credentials_without_network_access():
    policy = http.UrlPolicy(frozenset({"api.example"}))
    with pytest.raises(http.SafeHttpError, match="rejected"):
        http._validate_url("https://user:secret@api.example/v1", policy)


def test_plaintext_non_loopback_is_rejected(monkeypatch):
    monkeypatch.setattr(
        http.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("203.0.113.10", 80))],
    )
    policy = http.UrlPolicy(
        frozenset({"api.example"}),
        allow_private_hosts=frozenset({"api.example"}),
        allow_http_loopback=True,
    )
    with pytest.raises(http.SafeHttpError, match="unencrypted"):
        http._validate_url("http://api.example/v1", policy)


def test_redirect_handler_fails_closed():
    handler = http._RejectRedirects()
    request = urllib.request.Request("https://api.example/v1")
    with pytest.raises(http.SafeHttpError, match="redirect"):
        handler.redirect_request(
            request, None, 302, "Found", {}, "https://other.example"
        )
