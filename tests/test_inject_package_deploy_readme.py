"""Regression tests for the fleet deployment README generator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "inject_package_deploy_readme.py"
)
SPEC = importlib.util.spec_from_file_location("inject_package_deploy_readme", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def test_block_uses_only_current_deployment_contract():
    block = generator._block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )

    assert "agent-utilities-deployment" in block
    assert "AgentConfig" in block
    assert "@sha256:<digest>" in block
    assert "agent-os-genesis" not in block
    assert ":latest" not in block
    assert "seeds secrets" not in block
    assert 'uv tool install "sample-agent[mcp]"' in block
    assert 'uv pip install -e ".[agent]"' in block
    assert ".[all]" not in block


def test_apply_is_idempotent_for_current_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Sample\n", encoding="utf-8")
    block = generator._block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )

    updated, changed = generator._apply(readme, block)
    assert changed is True
    readme.write_text(updated, encoding="utf-8")
    unchanged, changed = generator._apply(readme, block)
    assert changed is False
    assert unchanged == updated
    assert updated.count(generator.BEGIN) == 1
    assert updated.count(generator.END) == 1


def test_additional_options_are_current_only_and_environment_neutral():
    block = generator._additional_block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )

    assert "authenticated HTTPS" in block
    assert "MCP_ALLOWED_HOSTS" in block
    assert "AgentConfig" in block
    assert ".arpa" not in block
    assert "behind Caddy" not in block
    assert "http://service" not in block


def test_apply_additional_updates_only_existing_markers():
    block = generator._additional_block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )
    stale = (
        f"# Sample\n\n{generator.ADDITIONAL_BEGIN}\n"
        "remote at http://sample-mcp.arpa/mcp\n"
        f"{generator.ADDITIONAL_END}\n"
    )

    updated, changed = generator._apply_additional(stale, block)
    assert changed is True
    assert updated.count(generator.ADDITIONAL_BEGIN) == 1
    assert ".arpa" not in updated
    assert generator._apply_additional("# No marker\n", block) == (
        "# No marker\n",
        False,
    )


def test_deployment_docs_are_current_reference_only_and_tls_bound():
    block = generator._docs_block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )

    assert "MCP_TOOL_MODE" in block and "intent" in block
    assert "AgentConfig" in block
    assert "authenticated HTTPS" in block
    assert "MCP_ALLOWED_HOSTS" in block
    assert "--cap-drop=ALL" in block
    assert "@sha256:<digest>" in block
    assert "https://service.example.invalid/mcp" in block
    assert "http://sample" not in block
    assert ".env" not in block
    assert "Caddy" not in block
    assert "Technitium" not in block


def test_apply_docs_updates_only_existing_markers():
    block = generator._docs_block(
        {
            "name": "sample",
            "package": "sample-agent",
            "image": "registry.example.invalid/sample-agent@sha256:<digest>",
        }
    )
    stale = (
        f"# Deployment\n\n{generator.DOCS_BEGIN}\n"
        "remote at http://sample.example.invalid/mcp behind Caddy\n"
        f"{generator.DOCS_END}\n"
    )

    updated, changed = generator._apply_docs(stale, block)
    assert changed is True
    assert updated.count(generator.DOCS_BEGIN) == 1
    assert "http://sample" not in updated
    assert generator._apply_docs("# No marker\n", block) == (
        "# No marker\n",
        False,
    )


def test_mutable_image_gate_scans_current_docs_and_assets_only(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docker").mkdir()
    (tmp_path / "README.md").write_text(
        "deploy registry.example.invalid/pkg:latest\n", encoding="utf-8"
    )
    (tmp_path / "CHANGELOG.md").write_text("historical :latest tag\n", encoding="utf-8")
    (tmp_path / "tests" / "fixture.json").write_text(
        '{"image":"fixture:latest"}\n', encoding="utf-8"
    )
    (tmp_path / "docker" / "compose.yml").write_text(
        "image: registry.example.invalid/pkg@sha256:<digest>\n", encoding="utf-8"
    )

    assert generator._mutable_image_references(tmp_path) == ["README.md:1"]


def test_legacy_tls_gate_requires_named_profiles_on_released_surfaces(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "tests").mkdir()
    package = tmp_path / "sample_agent"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / ".env.example").write_text("SAMPLE_SSL_VERIFY=True\n", encoding="utf-8")
    (tmp_path / "docs" / "usage.md").write_text("Api(verify=False)\n", encoding="utf-8")
    (package / "client.py").write_text(
        "def connect(verify: bool = True): ...\n", encoding="utf-8"
    )
    (tmp_path / "tests" / "fixture.py").write_text(
        "client.verify = False\n", encoding="utf-8"
    )

    assert generator._legacy_tls_boolean_references(tmp_path) == [
        ".env.example:1",
        "docs/usage.md:1",
        "sample_agent/client.py:1",
    ]

    (tmp_path / ".env.example").write_text(
        "SAMPLE_TLS_PROFILE=system\nSAMPLE_TLS_PROFILE_REF=\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "usage.md").write_text(
        "TLS policy is resolved through AgentConfig.\n", encoding="utf-8"
    )
    (package / "client.py").write_text(
        "def connect(tls_profile): ...\n", encoding="utf-8"
    )

    assert generator._legacy_tls_boolean_references(tmp_path) == []
