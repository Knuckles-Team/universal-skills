"""Fail-closed stdlib HTTP boundary for standalone skills.

The helper deliberately disables redirects and ambient proxies, accepts only exact
configured hosts, bounds every response, and obtains TLS trust exclusively from the
runtime certificate environment.  It never persists or includes a URL, credential,
response body, or local certificate path in an exception.
"""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import ssl
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

MAX_URL_CHARS = 8_192
MAX_HOSTS = 32
MAX_DNS_ANSWERS = 32
DEFAULT_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MIN_TIMEOUT_SECONDS = 0.1
MAX_TIMEOUT_SECONDS = 120.0


class SafeHttpError(RuntimeError):
    """An outbound request failed without reflecting sensitive context."""


class SafeHttpStatus(SafeHttpError):
    """The remote service returned a non-success status."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"remote service returned HTTP {status}")


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class UrlPolicy:
    """Exact-host egress policy.

    ``allow_private_hosts`` is an explicit set of configured internal destinations.
    Plain HTTP remains limited to loopback even for those hosts.
    """

    allowed_hosts: frozenset[str]
    allow_private_hosts: frozenset[str] = frozenset()
    allow_http_loopback: bool = False

    def __post_init__(self) -> None:
        allowed = _normalize_hosts(self.allowed_hosts)
        private = _normalize_hosts(self.allow_private_hosts)
        if not allowed or not private.issubset(allowed):
            raise ValueError("HTTP host policy is invalid")
        object.__setattr__(self, "allowed_hosts", allowed)
        object.__setattr__(self, "allow_private_hosts", private)


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise SafeHttpError("remote redirect was rejected")


def _normalize_hosts(values: frozenset[str]) -> frozenset[str]:
    if len(values) > MAX_HOSTS:
        raise ValueError("HTTP host policy is too large")
    normalized: set[str] = set()
    for raw in values:
        value = str(raw).strip().lower().rstrip(".")
        try:
            value.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("HTTP host policy is invalid") from None
        if (
            not value
            or len(value) > 253
            or any(character in value for character in "/@*?#[]")
            or any(ord(character) < 33 for character in value)
        ):
            raise ValueError("HTTP host policy is invalid")
        try:
            ipaddress.ip_address(value)
        except ValueError:
            labels = value.split(".")
            if any(
                not label
                or len(label) > 63
                or label.startswith("-")
                or label.endswith("-")
                or not all(
                    character.isalnum() or character == "-" for character in label
                )
                for label in labels
            ):
                raise ValueError("HTTP host policy is invalid") from None
        normalized.add(value)
    return frozenset(normalized)


def _addresses(
    host: str, port: int
) -> tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, ...]:
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError:
        raise SafeHttpError("remote DNS resolution failed") from None
    addresses: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for count, answer in enumerate(answers, 1):
        if count > MAX_DNS_ANSWERS:
            raise SafeHttpError("remote DNS response exceeded its safe boundary")
        try:
            address = ipaddress.ip_address(str(answer[4][0]))
        except (IndexError, TypeError, ValueError):
            raise SafeHttpError("remote DNS response was invalid") from None
        if address not in addresses:
            addresses.append(address)
    if not addresses:
        raise SafeHttpError("remote DNS resolution returned no address")
    return tuple(addresses)


def _validate_url(url: str, policy: UrlPolicy) -> tuple[str, str, int]:
    if not isinstance(url, str) or not url or len(url) > MAX_URL_CHARS:
        raise SafeHttpError("remote URL was rejected")
    try:
        parsed = urlsplit(url)
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    except ValueError:
        raise SafeHttpError("remote URL was rejected") from None
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        scheme not in {"http", "https"}
        or host not in policy.allowed_hosts
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or not (1 <= port <= 65_535)
    ):
        raise SafeHttpError("remote URL was rejected")
    addresses = _addresses(host, port)
    if host not in policy.allow_private_hosts and any(
        not address.is_global for address in addresses
    ):
        raise SafeHttpError("remote destination was rejected")
    if scheme == "http":
        if not policy.allow_http_loopback or any(
            not address.is_loopback for address in addresses
        ):
            raise SafeHttpError("unencrypted remote transport was rejected")
    return scheme, host, port


def _tls_context() -> ssl.SSLContext:
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    capath = os.environ.get("SSL_CERT_DIR")
    try:
        return ssl.create_default_context(cafile=cafile or None, capath=capath or None)
    except (OSError, ssl.SSLError):
        raise SafeHttpError("runtime TLS trust configuration is invalid") from None


def _bounded_timeout(timeout: float) -> float:
    try:
        value = float(timeout)
    except (TypeError, ValueError):
        raise SafeHttpError("remote timeout is invalid") from None
    if not MIN_TIMEOUT_SECONDS <= value <= MAX_TIMEOUT_SECONDS:
        raise SafeHttpError("remote timeout is outside its safe boundary")
    return value


def open_bounded(
    request: str | urllib.request.Request,
    *,
    policy: UrlPolicy,
    timeout: float = 30.0,
    max_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> HttpResponse:
    """Execute one non-redirecting request and return a bounded response."""

    if not isinstance(max_bytes, int) or not 1 <= max_bytes <= 64 * 1024 * 1024:
        raise SafeHttpError("remote response boundary is invalid")
    prepared = (
        request
        if isinstance(request, urllib.request.Request)
        else urllib.request.Request(request)
    )
    original_url = prepared.full_url
    _validate_url(original_url, policy)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=_tls_context()),
        _RejectRedirects(),
    )
    try:
        with opener.open(prepared, timeout=_bounded_timeout(timeout)) as response:
            final_url = response.geturl()
            _validate_url(final_url, policy)
            if (
                urlsplit(final_url).netloc.casefold()
                != urlsplit(original_url).netloc.casefold()
            ):
                raise SafeHttpError("remote origin changed during request")
            status = int(getattr(response, "status", 0))
            if not 200 <= status < 300:
                raise SafeHttpStatus(status)
            declared = response.headers.get("Content-Length")
            if declared:
                try:
                    if int(declared) > max_bytes:
                        raise SafeHttpError(
                            "remote response exceeded its safe boundary"
                        )
                except ValueError:
                    raise SafeHttpError("remote response length was invalid") from None
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise SafeHttpError("remote response exceeded its safe boundary")
            return HttpResponse(
                status=status, headers=dict(response.headers), body=body
            )
    except SafeHttpError:
        raise
    except urllib.error.HTTPError as exc:
        raise SafeHttpStatus(int(exc.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError):
        raise SafeHttpError("remote service is unavailable") from None


def open_json(
    request: str | urllib.request.Request,
    *,
    policy: UrlPolicy,
    timeout: float = 30.0,
    max_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> tuple[Any, HttpResponse]:
    """Execute a request and decode one bounded JSON document."""

    response = open_bounded(
        request,
        policy=policy,
        timeout=timeout,
        max_bytes=max_bytes,
    )
    if not response.body:
        return None, response
    try:
        payload = json.loads(response.body)
    except (UnicodeError, json.JSONDecodeError):
        raise SafeHttpError("remote response was not valid JSON") from None
    return payload, response
