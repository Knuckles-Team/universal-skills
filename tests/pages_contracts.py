"""Offline Pages contracts; only this checkout and disposable build output."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

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
        "spec-generator",
        "task-planner",
        "spec-verifier",
        "sdd-full-lifecycle",
    ):
        assert f"/{skill}/SKILL.md" in guide
    page = checkout / "site/specs/US-PAGES-001/spec/index.html"
    output = page.read_text()
    assert "SPECIFIED" in output and "NOT_AUDITED" in output
    assert "Acceptance evidence pending" in output
    for link in ("../plan/", "../test-spec/", "../tasks/"):
        assert f'href="{link}"' in output
    spec = checkout / "specs/US-PAGES-001/spec.md"
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
    package = checkout / "specs/US-PAGES-001"
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
    assert "US-PAGES-001" in result.stderr or "absent.md" in result.stderr


def test_synthetic_accepted_receipts(checkout):
    package = checkout / "specs/US-PAGES-001"
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
    output = (checkout / "site/specs/US-PAGES-001/spec/index.html").read_text()
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
