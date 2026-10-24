"""Validate declared OpenAPI security without inferring public access or credentials."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_TYPES = {"apiKey", "http", "oauth2", "openIdConnect", "mutualTLS"}
_FLOW_URLS = {
    "implicit": ("authorizationUrl",),
    "password": ("tokenUrl",),
    "clientCredentials": ("tokenUrl",),
    "authorizationCode": ("authorizationUrl", "tokenUrl"),
}


def _object(value, label):
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object with string keys")
    return value


def _string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")


def _version(openapi_version):
    if not isinstance(openapi_version, str) or not re.fullmatch(
        r"3\.[01]\.\d+(?:[-+][A-Za-z0-9.-]+)?", openapi_version
    ):
        raise ValueError("Security validation supports OpenAPI 3.0 and 3.1")
    return openapi_version.startswith("3.0.")


def _url(value, label):
    _string(value, label)
    if any(character.isspace() or ord(character) < 32 for character in value):
        raise ValueError(f"{label} must be a URL without whitespace or controls")
    try:
        parsed = urlsplit(value)
        if parsed.scheme and (
            parsed.scheme not in {"http", "https"} or not parsed.netloc
        ):
            raise ValueError("Invalid URL scheme or authority")
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid URL reference") from exc


def _flows(value):
    for name, flow in _object(value, "OAuth flows").items():
        if name.startswith("x-"):
            continue
        if name not in _FLOW_URLS:
            raise ValueError("Unsupported OAuth flow name")
        flow = _object(flow, "OAuth flow")
        if "$ref" in flow:
            raise ValueError("OAuth flow references require an explicit adapter")
        for field in _FLOW_URLS[name]:
            _url(flow.get(field), field)
        if "refreshUrl" in flow:
            _url(flow["refreshUrl"], "refreshUrl")
        scopes = _object(flow.get("scopes"), "OAuth scopes")
        if not all(isinstance(description, str) for description in scopes.values()):
            raise ValueError("OAuth scope descriptions must be strings")


def _scheme(definition, *, legacy):
    definition = _object(definition, "Security scheme")
    if "$ref" in definition:
        raise ValueError("Security scheme references require an explicit adapter")
    kind = definition.get("type")
    if not isinstance(kind, str) or kind not in _TYPES:
        raise ValueError("Unsupported or missing security scheme type")
    for field in ("description", "bearerFormat"):
        if field in definition and not isinstance(definition[field], str):
            raise ValueError(f"Security scheme {field} must be a string")
    _scheme_fields(definition, kind, legacy=legacy)


def _scheme_fields(definition, kind, *, legacy):
    if kind == "apiKey":
        _string(definition.get("name"), "API key name")
        if definition.get("in") not in ("query", "header", "cookie"):
            raise ValueError("API key location must be query, header or cookie")
    elif kind == "http":
        scheme = definition.get("scheme")
        _string(scheme, "HTTP authentication scheme")
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", scheme):
            raise ValueError("HTTP authentication scheme must be a token")
    elif kind == "oauth2":
        _flows(definition.get("flows"))
    elif kind == "openIdConnect":
        _url(definition.get("openIdConnectUrl"), "OpenID Connect URL")
    elif legacy:
        raise ValueError("mutualTLS requires OpenAPI 3.1")


def validate_requirements(requirements, schemes, *, openapi_version):
    """Return a validated security array unchanged; ``schemes`` must be validated.

    An empty array and an empty alternative are distinct valid declarations.
    Schemes within an alternative are ANDed; alternatives are ORed. This checks
    declaration shape, not whether the runtime supports its credential types.
    """
    legacy = _version(openapi_version)
    _object(schemes, "Security schemes")
    if not isinstance(requirements, list):
        raise ValueError("Security requirements must be an array")
    for alternative in requirements:
        for name, scopes in _object(alternative, "Security requirement").items():
            _requirement(name, scopes, schemes, legacy=legacy)
    return requirements


def validate_security(document):
    """Return declared schemes after checking every explicit root/operation value.

    Missing security remains missing; this function does not classify it as public.
    An explicit root declaration is checked even when every operation overrides it.
    """
    _object(document, "OpenAPI document")
    version = document.get("openapi")
    legacy = _version(version)
    components = _object(document.get("components", {}), "OpenAPI components")
    schemes = _object(components.get("securitySchemes", {}), "Security schemes")
    for name, definition in schemes.items():
        if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
            raise ValueError("Invalid security scheme component name")
        _scheme(definition, legacy=legacy)
    if "security" in document:
        validate_requirements(document["security"], schemes, openapi_version=version)
    paths = _object(document.get("paths", {}), "OpenAPI paths")
    for item in paths.values():
        for method, operation in _object(item, "OpenAPI path item").items():
            if method not in _METHODS:
                continue
            _object(operation, "OpenAPI operation")
            if "security" in operation:
                validate_requirements(
                    operation["security"], schemes, openapi_version=version
                )
    return schemes


def _requirement(name, scopes, schemes, *, legacy):
    if name not in schemes:
        raise ValueError("Security requirement names an undeclared scheme")
    if not isinstance(scopes, list) or not all(
        isinstance(scope, str) for scope in scopes
    ):
        raise ValueError(
            "Security requirement scopes or roles must be an array of strings"
        )
    if legacy and scopes and schemes[name]["type"] not in {"oauth2", "openIdConnect"}:
        raise ValueError("OpenAPI 3.0 non-OAuth requirements must have empty scopes")
