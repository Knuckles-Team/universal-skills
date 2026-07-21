from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = PROJECT_ROOT / "universal_skills" / "research" / "web-crawler" / "scripts"


def _runtime():
    pytest.importorskip("agent_utilities")
    sys.path.insert(0, str(SCRIPT_DIR))
    return importlib.import_module("security_runtime")


def _policy(tmp_path: Path):
    runtime = _runtime()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return runtime.CrawlerSecurityPolicy(
        allowed_private_hosts=frozenset(),
        allowed_redirect_hosts=frozenset(),
        max_response_bytes=1024 * 1024,
        max_redirects=2,
        allow_browser_fetch=False,
        workspace_root=workspace,
        output_root=tmp_path / "xdg" / "web-crawler",
    )


def test_crawler_source_has_no_insecure_transport_or_browser_switches() -> None:
    source = (SCRIPT_DIR / "crawl.py").read_text(encoding="utf-8")
    assert "--insecure" not in source
    assert "CERT_NONE" not in source
    assert "verify=False" not in source
    assert '"--no-sandbox"' not in source
    assert "requests.get(" not in source
    assert "process_iframes=False" in source
    assert "--host-resolver-rules=" in (SCRIPT_DIR / "security_runtime.py").read_text(
        encoding="utf-8"
    )
    assert "source_http_allow_browser_fetch" in (
        SCRIPT_DIR / "security_runtime.py"
    ).read_text(encoding="utf-8")


def test_private_seed_is_rejected_without_explicit_allowlist(tmp_path: Path) -> None:
    runtime = _runtime()
    policy = _policy(tmp_path)
    with pytest.raises(runtime.CrawlerSecurityError):
        policy.validate_url("http://127.0.0.1/resource", resolve_dns=False)


def test_discovered_cross_origin_url_is_rejected(tmp_path: Path) -> None:
    runtime = _runtime()
    policy = _policy(tmp_path)
    with pytest.raises(runtime.CrawlerSecurityError):
        policy.require_scoped_url(
            "https://other.example/resource",
            allowed_origins={"https://source.example:443"},
            resolve_dns=False,
        )


def test_output_is_confined_and_written_with_opaque_filename(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    output = policy.resolve_output_dir("crawl-output")
    assert output is not None
    assert output.is_relative_to(policy.workspace_root)
    assert policy.write_markdown(
        output,
        "contact: person@example.com",
        "https://source.example/docs/page",
    )
    files = list(output.glob("*.md"))
    assert len(files) == 1
    assert files[0].name.startswith("page-")
    assert "source.example" not in files[0].name
    assert "person@example.com" not in files[0].read_text(encoding="utf-8")


def test_output_escape_and_symlink_are_rejected(tmp_path: Path) -> None:
    runtime = _runtime()
    policy = _policy(tmp_path)
    with pytest.raises(runtime.CrawlerSecurityError):
        policy.resolve_output_dir("../outside")

    link = policy.workspace_root / "linked-output"
    target = tmp_path / "external"
    target.mkdir()
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")
    with pytest.raises(runtime.CrawlerSecurityError):
        policy.resolve_output_dir("linked-output")


def test_kg_endpoint_rejects_query_and_oversized_token(tmp_path: Path) -> None:
    runtime = _runtime()
    policy = _policy(tmp_path)
    with pytest.raises(runtime.CrawlerSecurityError):
        runtime.SafeMCPClient(
            "https://graph.example/mcp?secret=value",
            policy=policy,
        )
    with pytest.raises(runtime.CrawlerSecurityError):
        runtime.SafeMCPClient(
            "https://graph.example/mcp",
            policy=policy,
            token="x" * (runtime.MAX_TOKEN_BYTES + 1),
        )


def test_aggregate_output_budget_fails_closed() -> None:
    runtime = _runtime()
    budget = runtime.OutputBudget(max_bytes=8, max_files=2)
    budget.consume(4)
    budget.consume(4)
    with pytest.raises(runtime.CrawlerSecurityError):
        budget.consume(1)
