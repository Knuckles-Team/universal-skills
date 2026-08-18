"""Focused security and determinism tests for the documentation readiness builder."""

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
    / "agent_readiness.py"
)
SCHEMA = SCRIPT.with_name("agent_readiness_schema.json")


def _load_generator():
    spec = importlib.util.spec_from_file_location("_agent_readiness_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "provider"
    (root / "docs").mkdir(parents=True)
    (root / "skills" / "provider-starter").mkdir(parents=True)
    (root / "skills" / "provider-starter" / "SKILL.md").write_text(
        "---\nname: provider-starter\ndescription: Test skill\n---\n\n# Skill\n",
        encoding="utf-8",
    )
    (root / "docs" / "index.md").write_text(
        "# Home\n\nA current package overview.\n", encoding="utf-8"
    )
    (root / "docs" / "guide.md").write_text(
        "# Guide\n\nUse the operator configuration references.\n", encoding="utf-8"
    )
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\n"
        "site_url: https://docs.example.invalid/\n"
        "nav:\n"
        "  - Home: index.md\n"
        "  - Guides:\n"
        "      - Guide: guide.md\n",
        encoding="utf-8",
    )
    readiness = {
        "schema_version": "agent-readiness/v1",
        "project": {"name": "provider", "kind": "package"},
        "applicability": {
            "content": True,
            "discoverability": True,
            "access_policy": True,
            "capabilities": True,
            "errors": False,
            "provenance": True,
            "measurement": False,
            "deployment": False,
        },
        "standards": [
            {"id": "RFC 3986", "kind": "rfc", "level": "normative"},
            {"id": "Docs Draft", "kind": "draft", "level": "draft"},
            {"id": "Concept IDs", "kind": "convention", "level": "advisory"},
        ],
        "content_signals": {"policy": "unset"},
        "budgets": {"curated_chars": 12_000, "summary_chars": 500, "full_chars": 8_000},
        "capabilities": {
            "api": {"applicable": False},
            "mcp": {"applicable": False},
            "a2a": {"applicable": False},
            "skills": {"applicable": True, "path": "skills"},
        },
    }
    applicability = root / "docs" / "agent-readiness.json"
    _write_json(applicability, readiness)
    return root, readiness


def _generated_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
        and (
            path.name in {"llms.txt", "llms-full.txt"}
            or path.name.endswith("manifest.json")
        )
    }


def test_generation_is_current_bounded_and_idempotent(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)

    first = module.generate(root)
    first_bytes = _generated_bytes(root)
    second = module.generate(root)

    assert first == second
    assert first_bytes == _generated_bytes(root)
    assert "llms.txt" in first["generated"]
    assert "llms-full.txt" not in first["generated"]
    assert (root / "llms-sections" / "guides" / "llms.txt").is_file()
    assert (root / "markdown-mirror-manifest.json").is_file()
    assert "Guide" in (root / "llms.txt").read_text(encoding="utf-8")
    assert "https://docs.example.invalid/guide/" in (root / "llms.txt").read_text(
        encoding="utf-8"
    )
    assert ".md" not in (root / "llms.txt").read_text(encoding="utf-8")

    # A removed navigation section is not retained as stale discovery context.
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/\n"
        "nav:\n  - Home: index.md\n",
        encoding="utf-8",
    )
    module.generate(root)
    assert not (root / "llms-sections" / "guides" / "llms.txt").exists()


def test_failed_late_plan_leaves_prior_outputs_byte_identical(tmp_path, monkeypatch):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    module.generate(root)
    before = _generated_bytes(root)

    def fail_after_source_validation(*args, **kwargs):
        raise module.ReadinessError("late-render-failure")

    monkeypatch.setattr(module, "_render_full", fail_after_source_validation)
    with pytest.raises(module.ReadinessError, match="late-render-failure"):
        module.generate(root, include_full=True, full_budget=8_000)
    assert before == _generated_bytes(root)


def test_mid_publish_failure_rolls_back_the_complete_artifact_set(
    tmp_path, monkeypatch
):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    module.generate(root)
    before = _generated_bytes(root)
    (root / "docs" / "guide.md").write_text(
        "# Guide\n\nChanged source that must not be partially published.\n",
        encoding="utf-8",
    )
    real_atomic_write = module._atomic_write
    failed = False

    def fail_one_replacement(path, payload):
        nonlocal failed
        if path.name == "markdown-mirror-manifest.json" and not failed:
            failed = True
            raise module.ReadinessError("injected-publish-failure")
        return real_atomic_write(path, payload)

    monkeypatch.setattr(module, "_atomic_write", fail_one_replacement)
    with pytest.raises(module.ReadinessError, match="injected-publish-failure"):
        module.generate(root)
    assert before == _generated_bytes(root)


def test_check_and_adoption_controls_output_ownership(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    (root / "llms.txt").write_text("operator-owned\n", encoding="utf-8")
    with pytest.raises(module.ReadinessError, match="output-unowned"):
        module.generate(root)
    assert (root / "llms.txt").read_text(encoding="utf-8") == "operator-owned\n"

    result = module.generate(root, check=True, adopt_existing=True)
    assert result["generated"]
    assert "llms.txt" in result["planned"]
    assert result["pruned"] == []
    assert (root / "llms.txt").read_text(encoding="utf-8") == "operator-owned\n"
    assert not (root / "agent-readiness-manifest.json").exists()
    module.generate(root, adopt_existing=True)
    assert (root / "llms.txt").read_text(encoding="utf-8") != "operator-owned\n"


def test_full_context_requires_explicit_budget_and_is_bounded(tmp_path):
    module = _load_generator()
    root, readiness = _fixture(tmp_path)
    readiness["budgets"]["full_chars"] = 100
    _write_json(root / "docs" / "agent-readiness.json", readiness)

    with pytest.raises(module.ReadinessError, match="full-context-oversize"):
        module.generate(root, include_full=True)
    readiness["budgets"]["full_chars"] = 8_000
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    result = module.generate(root, include_full=True, full_budget=8_000)
    assert "llms-full.txt" in result["generated"]


def test_nested_index_sources_map_to_static_directory_urls(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    (root / "docs" / "nested").mkdir()
    (root / "docs" / "nested" / "index.md").write_text(
        "# Nested\n\nNested source.\n", encoding="utf-8"
    )
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/base/\n"
        "nav:\n"
        "  - Home: index.md\n"
        "  - Guides:\n"
        "      - Guide: guide.md\n"
        "      - Nested: nested/index.md\n",
        encoding="utf-8",
    )
    module.generate(root)
    mirror = json.loads(
        (root / "markdown-mirror-manifest.json").read_text(encoding="utf-8")
    )
    urls = {entry["source"]: entry["url"] for entry in mirror["entries"]}
    markdown_urls = {
        entry["source"]: entry["markdown_url"] for entry in mirror["entries"]
    }
    assert urls["docs/index.md"] == "https://docs.example.invalid/base/"
    assert urls["docs/nested/index.md"] == "https://docs.example.invalid/base/nested/"
    assert (
        markdown_urls["docs/index.md"] == "https://docs.example.invalid/base/index.md"
    )
    assert (
        markdown_urls["docs/nested/index.md"]
        == "https://docs.example.invalid/base/nested/index.md"
    )
    assert (
        markdown_urls["docs/guide.md"]
        == "https://docs.example.invalid/base/guide/index.md"
    )
    assert all(not url.endswith(".md") for url in urls.values())


def test_site_url_requires_a_directory_style_path(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/base\n"
        "nav:\n  - Home: index.md\n",
        encoding="utf-8",
    )
    with pytest.raises(module.ReadinessError, match="url-invalid"):
        module.generate(root)


def test_source_route_and_index_collisions_fail_closed(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    (root / "docs" / "guide").mkdir()
    (root / "docs" / "guide" / "index.md").write_text(
        "# Guide index\n\nDuplicate route.\n", encoding="utf-8"
    )
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/\n"
        "nav:\n"
        "  - Home: index.md\n"
        "  - Guide: guide.md\n"
        "  - Guide Index: guide/index.md\n",
        encoding="utf-8",
    )
    with pytest.raises(module.ReadinessError, match="url-duplicate"):
        module.generate(root)


@pytest.mark.parametrize(
    "mkdocs",
    [
        "site_name: Provider\nsite_url: https://docs.example.invalid/\nnav: []\n",
        "site_name: Provider\nsite_url: https://docs.example.invalid/\nnav: [{Bad: [1]}]\n",
        "site_name: Provider\nsite_url: https://docs.example.invalid/\nnav: [{Home: ../outside.md}]\n",
    ],
)
def test_malformed_navigation_and_traversal_fail_closed(tmp_path, mkdocs):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    (root / "mkdocs.yml").write_text(mkdocs, encoding="utf-8")
    with pytest.raises(module.ReadinessError):
        module.generate(root)


def test_symlink_duplicate_and_output_safety_fail_closed(tmp_path):
    module = _load_generator()
    root, _ = _fixture(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    (root / "docs" / "link.md").symlink_to(outside)
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/\n"
        "nav:\n  - Link: link.md\n",
        encoding="utf-8",
    )
    with pytest.raises(module.ReadinessError, match="symlink"):
        module.generate(root)

    (root / "docs" / "link.md").unlink()
    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/\n"
        "nav:\n  - One: index.md\n  - Same: index.md\n",
        encoding="utf-8",
    )
    with pytest.raises(module.ReadinessError, match="duplicate"):
        module.generate(root)

    (root / "mkdocs.yml").write_text(
        "site_name: Provider\nsite_url: https://docs.example.invalid/\n"
        "nav:\n  - Home: index.md\n",
        encoding="utf-8",
    )
    (root / "llms.txt").symlink_to(outside)
    with pytest.raises(module.ReadinessError, match="output-symlink"):
        module.generate(root)


def test_secret_private_endpoint_and_false_capability_claims_are_rejected(tmp_path):
    module = _load_generator()
    root, readiness = _fixture(tmp_path)
    (root / "docs" / "index.md").write_text(
        "# Home\n\nAPI_KEY=abcdefghijklmnop\n", encoding="utf-8"
    )
    with pytest.raises(module.ReadinessError, match="secret-like"):
        module.generate(root)

    (root / "docs" / "index.md").write_text(
        '{"AWS_SECRET_ACCESS_KEY": "abcdefghijklmnop"}\n', encoding="utf-8"
    )
    with pytest.raises(module.ReadinessError, match="secret-like"):
        module.generate(root)

    (root / "docs" / "index.md").write_text("# Home\n\nSafe text.\n", encoding="utf-8")
    artifact = root / "mcp.json"
    _write_json(artifact, {"applicable": True})
    readiness["capabilities"]["mcp"] = {
        "applicable": True,
        "artifact": "mcp.json",
        "endpoint": "https://docs.example.invalid/mcp",
    }
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    with pytest.raises(module.ReadinessError, match="artifact-schema"):
        module.generate(root)

    _write_json(
        artifact,
        {"applicable": True, "surface": "mcp", "source": "docs/index.md"},
    )
    readiness["capabilities"]["mcp"] = {
        "applicable": True,
        "artifact": "mcp.json",
        "endpoint": "https://127.0.0.1/mcp",
    }
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    with pytest.raises(module.ReadinessError, match="private-url"):
        module.generate(root)

    readiness["project"]["kind"] = "library"
    readiness["capabilities"]["mcp"]["endpoint"] = "https://docs.example.invalid/mcp"
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    with pytest.raises(module.ReadinessError, match="library-capability"):
        module.generate(root)


def test_capability_provenance_binds_artifact_and_source_digests(tmp_path):
    module = _load_generator()
    root, readiness = _fixture(tmp_path)
    source = root / "provider.py"
    source.write_text("def serve():\n    return 'ready'\n", encoding="utf-8")
    artifact = root / "mcp.json"
    _write_json(
        artifact,
        {"applicable": True, "surface": "mcp", "source": "provider.py"},
    )
    readiness["capabilities"]["mcp"] = {
        "applicable": True,
        "artifact": "mcp.json",
        "endpoint": "https://docs.example.invalid/mcp/",
    }
    _write_json(root / "docs" / "agent-readiness.json", readiness)

    result = module.generate(root)
    evidence = result["capability_evidence"]["mcp"]
    assert evidence["artifact"] == "mcp.json"
    assert evidence["source"] == "provider.py"
    assert len(evidence["artifact_sha256"]) == 64
    assert len(evidence["source_sha256"]) == 64


def test_maturity_content_signal_and_schema_contracts_are_explicit(tmp_path):
    module = _load_generator()
    root, readiness = _fixture(tmp_path)
    readiness["standards"][0]["level"] = "advisory"
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    with pytest.raises(module.ReadinessError, match="maturity-rfc-level"):
        module.generate(root)

    readiness["standards"][0]["level"] = "normative"
    readiness.pop("content_signals")
    _write_json(root / "docs" / "agent-readiness.json", readiness)
    with pytest.raises(module.ReadinessError, match="content-signals"):
        module.generate(root)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"].endswith("agent-readiness-v1.json")
    assert schema["properties"]["content_signals"]["properties"]["policy"]["enum"] == [
        "unset",
        "operator-reviewed",
    ]


def test_generator_is_source_only_and_does_not_scrape_html_or_import_runtime():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "importlib.import_module" not in source
    assert "mkdocs build" not in source
    assert "BeautifulSoup" not in source
    assert "generated HTML" in source


def test_builder_scaffold_carries_the_readiness_contract(tmp_path):
    scaffold_path = SCRIPT.with_name("scaffold_package.py")
    spec = importlib.util.spec_from_file_location(
        "_readiness_scaffold_test", scaffold_path
    )
    assert spec and spec.loader
    scaffold = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scaffold
    spec.loader.exec_module(scaffold)

    scaffold.scaffold("readiness-provider", output_dir=str(tmp_path))
    root = tmp_path / "readiness-provider"
    assert (root / "docs" / "agent-readiness.json").is_file()
    assert (root / "docs" / "agent-readiness.schema.json").is_file()
    assert (root / "scripts" / "generate_agent_readiness.py").is_file()
    assert (root / "llms.txt").is_file()
    manifest = json.loads(
        (root / "agent-readiness-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["content_signals"] == {"policy": "unset"}
    assert manifest["capabilities"]["mcp"]["applicable"] is True
