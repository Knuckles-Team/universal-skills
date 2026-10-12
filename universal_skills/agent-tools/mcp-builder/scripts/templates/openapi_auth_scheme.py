"""Typed, declared provider authentication backed by SDK credential references."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AuthKind(StrEnum):
    """Supported wire representations; neither implies provider permissions."""

    BEARER = "bearer"
    HEADER = "header"


@dataclass(frozen=True)
class ProviderAuthScheme:
    """One named OpenAPI scheme, never a credential value or a default header."""

    name: str
    kind: AuthKind
    header: str = ""


def declared_scheme(
    name: str, definitions: Mapping[str, Any]
) -> ProviderAuthScheme | None:
    """Fail closed for an explicit unknown or unsupported scheme."""
    if not name:
        return None
    if name not in definitions:
        raise ValueError("Selected authentication scheme is not declared")
    definition = definitions[name]
    if not isinstance(definition, Mapping):
        raise TypeError("Authentication scheme must be an OpenAPI object")
    wire_scheme = definition.get("scheme", "")
    if (
        definition.get("type") == "http"
        and isinstance(wire_scheme, str)
        and wire_scheme.casefold() == "bearer"
    ):
        return ProviderAuthScheme(name, AuthKind.BEARER)
    return ProviderAuthScheme(name, AuthKind.HEADER, _credential_header(definition))


def _credential_header(definition: Mapping[str, Any]) -> str:
    """Validate a header credential independently of bearer selection."""
    if definition.get("type") != "apiKey" or definition.get("in") != "header":
        raise ValueError("Unsupported provider authentication scheme")
    header = definition.get("name")
    if not isinstance(header, str) or not re.fullmatch(
        r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", header
    ):
        raise ValueError("Invalid credential header name")
    if header.casefold() in {
        "host",
        "connection",
        "content-length",
        "transfer-encoding",
        "proxy-authorization",
        "proxy-authenticate",
        "cookie",
    }:
        raise ValueError("Credential header conflicts with HTTP transport")
    return header


def credential_headers(definitions: Mapping[str, Any]) -> set[str]:
    """Reserve every declared credential header, including on public operations."""
    return {"authorization", "cookie", "host", "x-api-key"} | {
        str(scheme.get("name", "")).casefold()
        for scheme in definitions.values()
        if scheme.get("type") == "apiKey" and scheme.get("in") == "header"
    }
