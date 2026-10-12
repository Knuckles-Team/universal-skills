"""Malformed declarations must never become an apparently public operation."""

import copy
import importlib
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
security = importlib.import_module("openapi_security")


@pytest.fixture
def document():
    return {
        "openapi": "3.0.4",
        "components": {
            "securitySchemes": {
                "key": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                "bearer": {"type": "http", "scheme": "bearer"},
                "oauth": {
                    "type": "oauth2",
                    "flows": {
                        "clientCredentials": {
                            "tokenUrl": "/token",
                            "scopes": {"read": "Read"},
                        }
                    },
                },
            }
        },
        "paths": {"/items": {"get": {"responses": {"204": {"description": "Empty"}}}}},
    }


@pytest.mark.parametrize(
    "requirements",
    [
        [],
        [{}],
        [{"key": []}],
        [{"key": [], "bearer": []}, {"oauth": ["read"]}],
        [{}, {"key": []}],
    ],
)
def test_valid_alternatives_are_preserved(document, requirements):
    document["security"] = requirements
    before = copy.deepcopy(document)
    schemes = security.validate_security(document)
    assert (
        security.validate_requirements(
            requirements, schemes, openapi_version=document["openapi"]
        )
        is requirements
    )
    assert document == before
    assert schemes is document["components"]["securitySchemes"]


@pytest.mark.parametrize(
    "requirements",
    [
        None,
        {},
        [None],
        [False],
        ["key"],
        [{"key": None}],
        [{"key": {}}],
        [{"key": "read"}],
        [{"key": [1]}],
        [{"unknown": []}],
        [{"key": ["admin"]}],
    ],
)
@pytest.mark.parametrize("location", ["root", "operation"])
def test_malformed_security_refused(document, requirements, location):
    target = document if location == "root" else document["paths"]["/items"]["get"]
    target["security"] = requirements
    with pytest.raises(ValueError):
        security.validate_security(document)


def test_malformed_root_is_not_hidden_by_operation_override(document):
    document["security"] = None
    document["paths"]["/items"]["get"]["security"] = []
    with pytest.raises(ValueError, match="array"):
        security.validate_security(document)


def test_missing_security_is_not_added(document):
    security.validate_security(document)
    assert "security" not in document
    assert "security" not in document["paths"]["/items"]["get"]


@pytest.mark.parametrize("version", ["3.1.0", "3.1.1"])
def test_31_permits_non_oauth_roles(document, version):
    document["openapi"] = version
    document["security"] = [{"key": ["operator"], "bearer": ["reader"]}]
    security.validate_security(document)


@pytest.mark.parametrize(
    "definition",
    [
        None,
        [],
        {},
        {"type": None},
        {"type": []},
        {"type": "unknown"},
        {"$ref": "#/components/securitySchemes/key"},
        {"type": "apiKey", "name": "X-Key"},
        {"type": "apiKey", "in": "header", "name": ""},
        {"type": "apiKey", "in": [], "name": "X-Key"},
        {"type": "http"},
        {"type": "http", "scheme": "not a token"},
        {"type": "http", "scheme": "bearer", "bearerFormat": None},
        {"type": "oauth2"},
        {"type": "oauth2", "flows": []},
        {"type": "oauth2", "flows": {"madeUp": {}}},
        {"type": "oauth2", "flows": {"implicit": {"scopes": {}}}},
        {
            "type": "oauth2",
            "flows": {"password": {"tokenUrl": "/token", "scopes": {"read": None}}},
        },
        {"type": "openIdConnect"},
        {"type": "openIdConnect", "openIdConnectUrl": "https://"},
        {"type": "mutualTLS"},
    ],
)
def test_malformed_or_unsupported_definitions_refused_even_when_unused(
    document, definition
):
    document["security"] = []
    document["components"]["securitySchemes"]["unused"] = definition
    with pytest.raises(ValueError):
        security.validate_security(document)


@pytest.mark.parametrize("value", [None, [], "invalid"])
def test_invalid_scheme_map_refused(document, value):
    document["components"]["securitySchemes"] = value
    with pytest.raises(ValueError):
        security.validate_security(document)


def test_all_oauth_flows_and_openid_are_preserved(document):
    flows = {
        "implicit": {
            "authorizationUrl": "https://example.test/authorize",
            "scopes": {},
        },
        "password": {"tokenUrl": "/token", "scopes": {}},
        "clientCredentials": {"tokenUrl": "/token", "scopes": {}},
        "authorizationCode": {
            "authorizationUrl": "/authorize",
            "tokenUrl": "/token",
            "refreshUrl": "/refresh",
            "scopes": {"read": ""},
        },
    }
    schemes = document["components"]["securitySchemes"]
    schemes["oauth"]["flows"] = flows
    schemes["oidc"] = {
        "type": "openIdConnect",
        "openIdConnectUrl": "https://example.test/.well-known/openid-configuration",
    }
    document["security"] = [{"oidc": ["openid"]}, {"oauth": ["read"]}]
    assert security.validate_security(document)["oauth"]["flows"] is flows


def test_31_mutual_tls_is_valid_but_not_inferred_supported(document):
    document["openapi"] = "3.1.1"
    document["components"]["securitySchemes"]["tls"] = {"type": "mutualTLS"}
    document["security"] = [{"tls": ["operator"]}]
    assert security.validate_security(document)["tls"] == {"type": "mutualTLS"}
