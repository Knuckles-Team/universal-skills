"""Offline Pages contracts; only this checkout and disposable build output."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def checkout(tmp_path):
    for name in ("mkdocs.yml", "CONTRIBUTING.md", "README.md", "AGENTS.md"):
        shutil.copy(ROOT / name, tmp_path / name)
    for name in ("docs", "specs"):
        shutil.copytree(ROOT / name, tmp_path / name)
    (tmp_path / "scripts").mkdir()
    shutil.copy(
        ROOT / "scripts/pages_sources.py", tmp_path / "scripts/pages_sources.py"
    )
    # Status is generated, never committed: give the copy the file a local
    # `pipelines-hook spec-status --write` would have produced.
    (tmp_path / "specs/pages/status.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "spec_id": "US-PAGES",
                "owner_repo": "universal-skills",
                "delivery_state": "SPECIFIED",
                "acceptance_state": "NOT_AUDITED",
                "evidence": [],
            }
        ),
        encoding="utf-8",
    )
    # Public skill links must resolve in this checkout, without importing skills.
    for source in (ROOT / "universal_skills").rglob("SKILL.md"):
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)
    return tmp_path


def build(checkout):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str(checkout / "site"),
        ],
        cwd=checkout,
        capture_output=True,
        text=True,
        check=False,
    )


def test_shared_pages_workflow_contract():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    )
    jobs = workflow["jobs"]
    pages_jobs = [
        job
        for job in jobs.values()
        if isinstance(job, dict)
        and job.get("uses")
        == "Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main"
    ]
    assert len(pages_jobs) == 1
    assert pages_jobs[0]["with"] == {
        "content_source": "docs",
        "shared_theme_enabled": True,
        "spec_dashboard_enabled": True,
        "spec_dashboard_config": ".config/spec-dashboard.json",
    }
    assert json.loads(
        (ROOT / ".config/spec-dashboard.json").read_text(encoding="utf-8")
    ) == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }


def test_shared_pages_triggers_and_generated_theme_assets_contract():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    )
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict)
    assert "workflow_dispatch" in triggers
    push = triggers["push"]
    assert push == {"tags": ["v*"]}

    generated_assets = (
        "docs/stylesheets/extra.css",
        "docs/assets/graph-mark.svg",
        "docs/assets/favicon.svg",
        "docs/assets/brands/epistemic-graph-logo-v1.png",
        "docs/assets/brands/agent-utilities-logo-v1.png",
        "docs/assets/brands/arbora-logo-v1.png",
        "docs/assets/brands/agent-connector-sdk-logo-v1.png",
        "docs/assets/brands/agent-webui-logo-v1.png",
        "docs/assets/brands/geniusbot-logo-v1.png",
        "docs/assets/brands/agent-terminal-ui-logo-v1.png",
        "docs/glossary.md",
    )
    for relative_path in generated_assets:
        generated = ROOT / relative_path
        assert generated.is_file(), relative_path
        assert generated.stat().st_size > 0, relative_path


def test_canonical_sources_and_existing_urls(checkout):
    result = build(checkout)
    assert result.returncode == 0, result.stderr
    for name in (
        "index.html",
        "overview/index.html",
        "contributing/index.html",
        "skill-catalog-audit/index.html",
        "skill-catalog-improvement-roadmap/index.html",
    ):
        assert (checkout / "site" / name).is_file(), name
    guide = (checkout / "site/contributing/index.html").read_text()
    for skill in (
        "speckit-specify",
        "speckit-tasks",
        "speckit-analyze",
        "sdd-full-lifecycle",
    ):
        assert f"/{skill}/SKILL.md" in guide
    page = checkout / "site/specs/pages/spec/index.html"
    output = page.read_text()
    assert "SPECIFIED" in output and "NOT_AUDITED" in output
    assert "Acceptance evidence pending" in output
    for link in ("../plan/", "../test-spec/", "../tasks/"):
        assert f'href="{link}"' in output
    spec = checkout / "specs/pages/spec.md"
    spec.write_text(spec.read_text() + "\nCanonical edit appears on rebuild.\n")
    contribution = checkout / "CONTRIBUTING.md"
    contribution.write_text(
        contribution.read_text() + "\nGuide edit appears on rebuild.\n"
    )
    result = build(checkout)
    assert result.returncode == 0, result.stderr
    assert "Canonical edit appears on rebuild" in page.read_text()
    assert (
        "Guide edit appears on rebuild"
        in (checkout / "site/contributing/index.html").read_text()
    )


@pytest.mark.parametrize(
    "failure",
    [
        "source",
        "link",
        "anchor",
        "status",
        "identity",
        "receipt",
        "nav",
        "evidence-type",
        "receipt-type",
        "short-commit",
        "private-receipt",
    ],
)
def test_invalid_sources_fail_closed(checkout, failure):
    package = checkout / "specs/pages"
    spec = package / "spec.md"
    status_path = package / "status.json"
    status = json.loads(status_path.read_text())
    if failure == "source":
        (package / "plan.md").unlink()
    elif failure == "link":
        spec.write_text(spec.read_text() + "\n[missing](missing.md)\n")
    elif failure == "anchor":
        spec.write_text(
            spec.read_text() + "\n[missing anchor](plan.md#absent-heading)\n"
        )
    elif failure == "nav":
        config = checkout / "mkdocs.yml"
        config.write_text(config.read_text() + "  - Missing: absent.md\n")
    else:
        if failure == "status":
            status["delivery_state"] = "UNKNOWN"
        elif failure == "identity":
            status["owner_repo"] = "another-repo"
        elif failure == "evidence-type":
            status["evidence"] = {}
        elif failure == "receipt-type":
            status["evidence"] = ["invalid"]
        elif failure in {"short-commit", "private-receipt"}:
            status["evidence"] = [
                {
                    "kind": "passing_acceptance",
                    "commit": "a" * (7 if failure == "short-commit" else 40),
                    "url": "https://example.invalid/private/result",
                }
            ]
        else:
            status["delivery_state"] = "IMPLEMENTED"
            status["acceptance_state"] = "ACCEPTED"
        status_path.write_text(json.dumps(status))
    result = build(checkout)
    assert result.returncode != 0, result.stdout
    assert "specs/pages" in result.stderr or "US-PAGES" in result.stderr or "absent.md" in result.stderr


def test_synthetic_accepted_receipts(checkout):
    package = checkout / "specs/pages"
    status_path = package / "status.json"
    status = json.loads(status_path.read_text())
    commit = "a" * 40
    prefix = "https://github.com/Knuckles-Team/universal-skills/"
    status.update(
        delivery_state="IMPLEMENTED",
        acceptance_state="ACCEPTED",
        evidence=[
            {
                "kind": "merged_implementation",
                "commit": commit,
                "url": f"{prefix}commit/{commit}",
            },
            {
                "kind": "passing_acceptance",
                "commit": commit,
                "url": f"{prefix}actions/runs/123",
            },
        ],
    )
    status_path.write_text(json.dumps(status))
    result = build(checkout)
    assert result.returncode == 0, result.stderr
    output = (checkout / "site/specs/pages/spec/index.html").read_text()
    assert f'href="{prefix}commit/{commit}"' in output
    assert f'href="{prefix}actions/runs/123"' in output
    assert "owner-reported metadata" in output
    assert "NOT_AUDITED" not in output
    assert "SPECIFIED" not in output
    status["evidence"][1]["commit"] = "b" * 40
    status_path.write_text(json.dumps(status))
    result = build(checkout)
    assert result.returncode != 0
    assert "matching implementation and acceptance receipts" in result.stderr


def test_build_without_generated_status(checkout):
    (checkout / "specs/pages/status.json").unlink()
    result = build(checkout)
    assert result.returncode == 0, result.stderr
    output = (checkout / "site/specs/pages/spec/index.html").read_text()
    assert "Owner-native status" not in output
