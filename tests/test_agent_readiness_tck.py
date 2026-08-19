"""Deterministic fixtures for the served Agent Readiness TCK boundary."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).parents[1]
    / "universal_skills"
    / "agent-tools"
    / "agent-package-builder"
    / "scripts"
    / "agent_readiness_tck.py"
)


def _load_tck():
    spec = importlib.util.spec_from_file_location("_agent_readiness_tck_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _response(module, status, content_type, body, **headers):
    response_headers = {"Content-Type": content_type, **headers}
    if not isinstance(body, (bytes, str)):
        body = json.dumps(body)
    return module.TckResponse(
        status=status,
        headers=response_headers,
        body=body.encode("utf-8") if isinstance(body, str) else body,
    )


def _problem_json(status=403, *, retryable=False):
    return json.dumps(
        {
            "type": "urn:agent-error:forbidden",
            "title": "Forbidden",
            "status": status,
            "detail": "The operation is not permitted.",
            "instance": "urn:agent-error-instance:test",
            "code": "forbidden",
            "retryable": retryable,
            "retry_after_s": 30 if retryable else None,
        }
    )


def _problem_markdown():
    return """---
status: 403
code: "forbidden"
type: "urn:agent-error:forbidden"
instance: "urn:agent-error-instance:test"
retryable: false
retry_after_s: null
---
# Forbidden

## Detail
> The operation is not permitted.
"""


def _passing_responses(module):
    link = (
        "<https://docs.example.invalid/.well-known/api-catalog>; "
        'rel="api-catalog"; type="application/linkset+json"'
    )
    markdown_headers = {
        "Vary": "Accept",
        "Cache-Control": "public, max-age=60",
        "Link": link,
    }
    responses = {
        ("/guide", module.MARKDOWN): _response(
            module,
            200,
            module.MARKDOWN,
            "# Guide\n\nCurrent Markdown.\n",
            **markdown_headers,
        ),
        ("/guide", module.HTML): _response(
            module,
            200,
            module.HTML,
            "<!doctype html><html><body>Current HTML</body></html>",
            **markdown_headers,
        ),
        (
            "/.well-known/api-catalog",
            module.LINKSET_JSON,
        ): _response(
            module,
            200,
            module.LINKSET_JSON,
            {
                "profile": module.API_CATALOG_PROFILE,
                "linkset": [
                    {
                        "anchor": ".",
                        "item": [{"href": "docs/capabilities/api.json"}],
                    }
                ],
            },
        ),
        (
            "/.well-known/mcp-server-card.json",
            "application/json",
        ): _response(
            module,
            200,
            "application/json",
            {
                "schema_version": "mcp-server-card/v1-experimental",
                "experimental": True,
                "transports": ["streamable-http"],
            },
        ),
        (
            "/.well-known/agent-skills.json",
            "application/json",
        ): _response(
            module,
            200,
            "application/json",
            {
                "schema_version": "agent-skills/v1",
                "skills": [
                    {
                        "name": "provider-starter",
                        "path": "skills/provider-starter/SKILL.md",
                    }
                ],
            },
        ),
        ("/a2a.json", "application/json"): _response(
            module,
            200,
            "application/json",
            {"name": "provider-agent", "type": "agent", "version": "0.1.0"},
        ),
        ("/errors/denied", module.PROBLEM_JSON): _response(
            module,
            403,
            module.PROBLEM_JSON,
            _problem_json(),
        ),
        ("/errors/denied", module.MARKDOWN): _response(
            module,
            403,
            module.MARKDOWN,
            _problem_markdown(),
        ),
        ("/private", module.PROBLEM_JSON): _response(
            module,
            403,
            module.PROBLEM_JSON,
            _problem_json(),
        ),
    }
    return responses


def test_fixture_contract_passes_with_bounded_structured_evidence():
    module = _load_tck()
    config = module.TckConfig(
        origin="https://docs.example.invalid",
        allowed_origins=("https://docs.example.invalid",),
        markdown_path="/guide",
        error_path="/errors/denied",
        discovery={
            "a2a_card": True,
            "agent_skills": True,
            "api_catalog": True,
            "mcp_server_card": True,
            "oauth_protected_resource": False,
        },
        security_paths=("/private",),
    )
    transport = module.FixtureTransport(_passing_responses(module))

    result = module.run_tck(config, transport=transport)
    evidence = result.to_dict()

    assert result.status == module.PASS
    assert evidence["schema_version"] == "agent-readiness-tck/v1"
    assert evidence["contract_version"] == "agent-readiness-tck/v1"
    assert evidence["maturity"] == "experimental"
    assert evidence["limits"]["authorization"] == "never-sent"
    assert evidence["limits"]["redirects"] == "rejected"
    assert any(
        check["id"] == "oauth-protected-resource"
        and check["status"] == module.NOT_APPLICABLE
        for check in evidence["checks"]
    )
    assert all("body" not in json.dumps(check) for check in evidence["checks"])
    assert transport.requests
    assert all("?" not in path for path, _ in transport.requests)


def test_malformed_and_stale_discovery_artifacts_fail_closed_without_body_evidence():
    module = _load_tck()
    responses = _passing_responses(module)
    responses[("/.well-known/api-catalog", module.LINKSET_JSON)] = _response(
        module,
        200,
        module.LINKSET_JSON,
        '{"profile":"https://www.rfc-editor.org/info/rfc9727",',
    )
    config = module.TckConfig(
        origin="https://docs.example.invalid",
        allowed_origins=("https://docs.example.invalid",),
        markdown_path="/guide",
        discovery={"api_catalog": True},
    )
    result = module.run_tck(config, transport=module.FixtureTransport(responses))
    api_check = next(check for check in result.checks if check["id"] == "api-catalog")
    assert result.status == module.FAIL
    assert api_check["reason"] == "malformed-json"
    assert "profile" not in json.dumps(api_check)

    responses[("/.well-known/api-catalog", module.LINKSET_JSON)] = _response(
        module,
        200,
        module.LINKSET_JSON,
        {"profile": "https://www.rfc-editor.org/info/rfc9726", "linkset": []},
    )
    stale = module.run_tck(config, transport=module.FixtureTransport(responses))
    assert next(check for check in stale.checks if check["id"] == "api-catalog")["reason"] == (
        "api-catalog-profile-stale"
    )


def test_unavailable_and_not_applicable_are_explicit_outcomes():
    module = _load_tck()
    unavailable_config = module.TckConfig(
        origin="https://docs.example.invalid",
        allowed_origins=("https://docs.example.invalid",),
        discovery={"mcp_server_card": True},
    )
    unavailable = module.run_tck(
        unavailable_config, transport=module.FixtureTransport({})
    )
    assert unavailable.status == module.UNAVAILABLE
    assert any(check["status"] == module.UNAVAILABLE for check in unavailable.checks)

    local_config = module.TckConfig(
        origin="http://127.0.0.1:8765",
        allowed_origins=("http://127.0.0.1:8765",),
        local_fixture=True,
        applicable=False,
    )
    not_applicable = module.run_tck(local_config)
    assert not_applicable.status == module.NOT_APPLICABLE
    assert not_applicable.checks[0]["reason"] == "surface-disabled"


def test_origin_and_secret_boundaries_are_fail_closed():
    module = _load_tck()
    with pytest.raises(module.TckConfigurationError, match="https"):
        module.TckConfig(
            origin="http://127.0.0.1",
            allowed_origins=("http://127.0.0.1",),
        )
    with pytest.raises(module.TckConfigurationError, match="private"):
        module.TckConfig(
            origin="https://127.0.0.1",
            allowed_origins=("https://127.0.0.1",),
        )
    with pytest.raises(module.TckConfigurationError, match="origin"):
        module.TckConfig(
            origin="https://docs.example.invalid/?token=not-recorded",
            allowed_origins=("https://docs.example.invalid/?token=not-recorded",),
        )


def test_size_link_and_denial_retry_budgets_fail():
    module = _load_tck()
    responses = _passing_responses(module)
    responses[("/guide", module.MARKDOWN)] = _response(
        module,
        200,
        module.MARKDOWN,
        "too-large",
        Vary="Accept",
        **{
            "Cache-Control": "public",
            "Link": (
                '<https://docs.example.invalid/a>; rel="api-catalog", '
                '<https://docs.example.invalid/b>; rel="describedby"'
            ),
        },
    )
    responses[("/private", module.PROBLEM_JSON)] = _response(
        module,
        403,
        module.PROBLEM_JSON,
        _problem_json(retryable=True),
    )
    config = module.TckConfig(
        origin="https://docs.example.invalid",
        allowed_origins=("https://docs.example.invalid",),
        markdown_path="/guide",
        max_response_bytes=4,
        max_links=1,
    )
    result = module.run_tck(config, transport=module.FixtureTransport(responses))
    checks = {check["id"]: check for check in result.checks}
    assert result.status == module.FAIL
    assert checks["markdown-negotiation"]["reason"] == "response-size-budget-exceeded"
    assert checks["link-budget"]["reason"] == "link-budget-exceeded"

    denial_config = module.TckConfig(
        origin="https://docs.example.invalid",
        allowed_origins=("https://docs.example.invalid",),
        markdown_path="/guide",
        security_paths=("/private",),
    )
    denial = module.run_tck(
        denial_config, transport=module.FixtureTransport(responses)
    )
    denial_checks = {check["id"]: check for check in denial.checks}
    assert denial_checks["auth-security:/private"]["reason"] == (
        "denial-marked-retryable"
    )
