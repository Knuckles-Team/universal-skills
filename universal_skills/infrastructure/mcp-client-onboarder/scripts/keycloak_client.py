#!/usr/bin/env python3
"""Minimal Keycloak machine-client provisioning (self-contained, urllib only).

Shared by the mcp-client-onboarder ``onboard``/``reap`` flows so the skill needs
no external Keycloak SDK. Creates/deletes confidential ``client_credentials``
clients carrying the ``mcp-fleet`` audience scope (so issued tokens get
``aud: mcp-fleet`` for the multiplexer's JWTVerifier).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://keycloak.arpa")
REALM = os.environ.get("KEYCLOAK_REALM", "homelab")
ADMIN_USER = os.environ.get("KEYCLOAK_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "")
FLEET_SCOPE = "mcp-fleet"


def _api(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{KEYCLOAK_URL}{path}", data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        return resp.status, resp.headers, (json.loads(raw) if raw else None)


def get_admin_token() -> str:
    data = urllib.parse.urlencode(
        {
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
            "grant_type": "password",
        }
    ).encode()
    req = urllib.request.Request(
        f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]


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
    except urllib.error.HTTPError as e:
        if e.code != 409:
            raise
    _, _, scopes = _api("GET", f"/admin/realms/{REALM}/client-scopes", token)
    return next(s["id"] for s in scopes if s["name"] == FLEET_SCOPE)


def _find_client(token, client_id):
    q = urllib.parse.quote(client_id)
    _, _, clients = _api("GET", f"/admin/realms/{REALM}/clients?clientId={q}", token)
    return clients[0] if clients else None


def create_client(client_id: str, token: str, token_lifespan: int = 28800) -> str:
    """Create (or reconcile) a confidential client_credentials client; return its secret."""
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
        uuid = existing["id"]
        _api("PUT", f"/admin/realms/{REALM}/clients/{uuid}", token, payload)
    else:
        try:
            _, headers, _ = _api(
                "POST", f"/admin/realms/{REALM}/clients", token, payload
            )
            uuid = headers.get("Location", "").rstrip("/").split("/")[-1]
        except urllib.error.HTTPError as e:
            if e.code != 409:
                raise
            uuid = _find_client(token, client_id)["id"]
    try:
        _api(
            "PUT",
            f"/admin/realms/{REALM}/clients/{uuid}/default-client-scopes/{scope_uuid}",
            token,
            {},
        )
    except urllib.error.HTTPError as e:
        if e.code not in (204, 409):
            raise
    _, _, secret = _api(
        "GET", f"/admin/realms/{REALM}/clients/{uuid}/client-secret", token
    )
    return (secret or {}).get("value", "N/A")


def delete_client(client_id: str, token: str) -> bool:
    """Delete a Keycloak client. Returns True if it existed."""
    existing = _find_client(token, client_id)
    if not existing:
        return False
    _api("DELETE", f"/admin/realms/{REALM}/clients/{existing['id']}", token)
    return True
