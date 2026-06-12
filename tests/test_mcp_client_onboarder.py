"""Tests for the mcp-client-onboarder rule generation + policy merge (pure logic).

Keycloak / Eunomia evaluation are exercised live elsewhere; these stay offline.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / (
    "universal_skills/infra/mcp-client-onboarder/scripts"
)


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, str(SCRIPTS / f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pr = _mod("policy_rules")

_BASE_POLICY = {
    "version": "1.0",
    "name": "t",
    "default_effect": "deny",
    "rules": [
        {"name": "_base-meta-tools", "effect": "allow", "principal_conditions": [],
         "resource_conditions": [], "actions": ["list", "execute"]},
        {"name": "claude-code-allow-all", "effect": "allow",
         "principal_conditions": [{"path": "uri", "operator": "equals", "value": "agent:claude-code"}],
         "resource_conditions": [], "actions": ["list", "execute"]},
    ],
}


def _policy(tmp_path):
    p = tmp_path / "policy.json"
    p.write_text(json.dumps(_BASE_POLICY))
    return p


def test_full_access_rule():
    rules = pr.build_rules("a", "full-access")
    assert len(rules) == 1
    assert rules[0]["actions"] == ["list", "execute"]
    assert rules[0]["resource_conditions"] == []
    assert rules[0]["principal_conditions"][0]["value"] == "agent:a"


def test_read_only_is_list_only():
    rules = pr.build_rules("a", "read-only")
    assert rules[0]["actions"] == ["list"]


def test_server_scoped_one_rule_per_server():
    rules = pr.build_rules("a", "server-scoped", servers=["github-mcp", "gitlab-mcp"])
    assert len(rules) == 2
    for r in rules:
        cond = r["resource_conditions"][0]
        assert cond["operator"] == "startswith" and cond["value"].endswith("__")


def test_server_scoped_requires_servers():
    with pytest.raises(ValueError):
        pr.build_rules("a", "server-scoped", servers=[])


def test_role_based_expands_roles_map():
    roles = {"devops": ["container-manager-mcp", "portainer-mcp"]}
    rules = pr.build_rules("a", "role-based", roles_map=roles, role="devops")
    assert len(rules) == 2


def test_upsert_is_idempotent_and_preserves_base(tmp_path):
    p = _policy(tmp_path)
    pr.upsert_client_rules(p, "ci", pr.build_rules("ci", "full-access"))
    pr.upsert_client_rules(p, "ci", pr.build_rules("ci", "full-access"))
    names = [r["name"] for r in json.loads(p.read_text())["rules"]]
    assert names.count("ci-full") == 1  # no duplicate
    assert "_base-meta-tools" in names and "claude-code-allow-all" in names


def test_remove_client_rules(tmp_path):
    p = _policy(tmp_path)
    pr.upsert_client_rules(p, "ci", pr.build_rules("ci", "full-access"))
    removed = pr.remove_client_rules(p, "ci")
    assert removed == 1
    names = [r["name"] for r in json.loads(p.read_text())["rules"]]
    assert "ci-full" not in names
    assert "_base-meta-tools" in names  # base untouched
