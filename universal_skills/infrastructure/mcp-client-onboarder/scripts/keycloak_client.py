#!/usr/bin/env python3
"""Minimal Keycloak machine-client provisioning (self-contained, urllib only).

Shared by the mcp-client-onboarder ``onboard``/``reap`` flows so the skill needs
no external Keycloak SDK. Creates/deletes confidential ``client_credentials``
clients carrying the configured audience claim for the multiplexer's JWT
verifier.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
from urllib.parse import urlsplit
from urllib.request import Request

from universal_skills._security.http import SafeHttpStatus, UrlPolicy, open_json

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "").rstrip("/")
REALM = os.environ.get("KEYCLOAK_REALM", "master")
ADMIN_REALM = os.environ.get("KEYCLOAK_ADMIN_REALM", "master")
ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "")
FLEET_SCOPE = os.environ.get("KEYCLOAK_AUDIENCE_SCOPE", "agent-services")
IDENTITY_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _identity(value: str, label: str) -> str:
    if not isinstance(value, str) or IDENTITY_RE.fullmatch(value) is None:
        raise RuntimeError(f"{label} is invalid")
    return value


def _policy() -> UrlPolicy:
    _identity(REALM, "realm")
    _identity(ADMIN_REALM, "administrator realm")
    _identity(FLEET_SCOPE, "audience scope")
    host = (urlsplit(KEYCLOAK_URL).hostname or "").lower().rstrip(".")
    return UrlPolicy(
        frozenset({host}),
        allow_private_hosts=frozenset({host}),
        allow_http_loopback=True,
    )


def _api(method, path, token=None, body=None):
    if not KEYCLOAK_URL:
        raise RuntimeError("KEYCLOAK_URL is required")
    if (
        method not in {"GET", "POST", "PUT", "DELETE"}
        or not isinstance(path, str)
        or not path.startswith("/")
        or path.startswith("//")
        or ".." in path
        or any(character in path for character in "\\\r\n#")
        or len(path) > 4_096
    ):
        raise RuntimeError("identity provider request path is invalid")
    if token is not None and (
        not isinstance(token, str) or not token or len(token) > 65_536
    ):
        raise RuntimeError("identity provider access token is invalid")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    if data is not None and len(data) > 1 * 1024 * 1024:
        raise RuntimeError("identity provider request exceeds its safe boundary")
    req = Request(
        f"{KEYCLOAK_URL}{path}", data=data, headers=headers, method=method
    )
    payload, response = open_json(
        req,
        policy=_policy(),
        timeout=15,
        max_bytes=8 * 1024 * 1024,
    )
    return response.status, response.headers, payload


def get_admin_token() -> str:
    if not KEYCLOAK_URL:
        raise RuntimeError("KEYCLOAK_URL is required")
    if (
        not ADMIN_USER
        or len(ADMIN_USER) > 256
        or any(character in ADMIN_USER for character in "\x00\r\n")
        or not ADMIN_PASS
        or len(ADMIN_PASS) > 65_536
        or any(character in ADMIN_PASS for character in "\x00\r\n")
    ):
        raise RuntimeError("identity provider administrator credential is invalid")
    data = urllib.parse.urlencode(
        {
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
            "grant_type": "password",
        }
    ).encode()
    req = Request(
        f"{KEYCLOAK_URL}/realms/{ADMIN_REALM}/protocol/openid-connect/token",
        data=data,
        method="POST",
    )
    payload, _ = open_json(
        req,
        policy=_policy(),
        timeout=15,
        max_bytes=1 * 1024 * 1024,
    )
    token = payload.get("access_token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token or len(token) > 65_536:
        raise RuntimeError("identity provider returned an invalid access token")
    return token


def _fleet_scope_uuid(token: str) -> str:
    _, _, scopes = _api("GET", f"/admin/realms/{REALM}/client-scopes", token)
    existing = next((s for s in (scopes or []) if s["name"] == FLEET_SCOPE), None)
    if existing:
        return existing["id"]
    payload = {
        "name": FLEET_SCOPE,
        "protocol": "openid-connect",
        "attributes": {"include.in.token.scope": "true"},
        "protocolMappers": [
            {
                "name": f"{FLEET_SCOPE}-audience",
                "protocol": "openid-connect",
                "protocolMapper": "oidc-audience-mapper",
                "config": {
                    "included.custom.audience": FLEET_SCOPE,
                    "access.token.claim": "true",
                    "id.token.claim": "false",
                },
            }
        ],
    }
    try:
        _api("POST", f"/admin/realms/{REALM}/client-scopes", token, payload)
    except SafeHttpStatus as e:
        if e.status != 409:
            raise
    _, _, scopes = _api("GET", f"/admin/realms/{REALM}/client-scopes", token)
    return next(s["id"] for s in scopes if s["name"] == FLEET_SCOPE)


def _find_client(token, client_id):
    q = urllib.parse.quote(_identity(client_id, "client identifier"), safe="")
    _, _, clients = _api("GET", f"/admin/realms/{REALM}/clients?clientId={q}", token)
    return clients[0] if clients else None


def create_client(client_id: str, token: str, token_lifespan: int = 28800) -> None:
    """Create or reconcile a confidential client without exporting its secret."""
    _identity(client_id, "client identifier")
    if not isinstance(token_lifespan, int) or not 60 <= token_lifespan <= 86_400:
        raise RuntimeError("token lifespan is outside its safe boundary")
    scope_uuid = _fleet_scope_uuid(token)
    payload = {
        "clientId": client_id,
        "name": client_id,
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "clientAuthenticatorType": "client-secret",
        "serviceAccountsEnabled": True,
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": False,
        "defaultClientScopes": [FLEET_SCOPE],
        "attributes": {"access.token.lifespan": str(token_lifespan)},
    }
    existing = _find_client(token, client_id)
    if existing:
        uuid = _identity(existing["id"], "client object identifier")
        _api("PUT", f"/admin/realms/{REALM}/clients/{uuid}", token, payload)
    else:
        try:
            _, headers, _ = _api(
                "POST", f"/admin/realms/{REALM}/clients", token, payload
            )
            uuid = _identity(
                headers.get("Location", "").rstrip("/").split("/")[-1],
                "client object identifier",
            )
        except SafeHttpStatus as e:
            if e.status != 409:
                raise
            uuid = _identity(
                _find_client(token, client_id)["id"], "client object identifier"
            )
    scope_uuid = _identity(scope_uuid, "scope object identifier")
    try:
        _api(
            "PUT",
            f"/admin/realms/{REALM}/clients/{uuid}/default-client-scopes/{scope_uuid}",
            token,
            {},
        )
    except SafeHttpStatus as e:
        if e.status not in (204, 409):
            raise


def delete_client(client_id: str, token: str) -> bool:
    """Delete a Keycloak client. Returns True if it existed."""
    existing = _find_client(token, client_id)
    if not existing:
        return False
    object_id = _identity(existing["id"], "client object identifier")
    _api("DELETE", f"/admin/realms/{REALM}/clients/{object_id}", token)
    return True
