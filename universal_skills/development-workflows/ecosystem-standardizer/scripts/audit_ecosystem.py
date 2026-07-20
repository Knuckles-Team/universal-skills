#!/usr/bin/env python3
"""Comprehensive ecosystem drift audit for agent-packages.

Scans all projects for structural compliance against the ecosystem standard,
producing a graded drift report with per-project scorecards.

Usage:
    python audit_ecosystem.py --agents-dir /path/to/agents --output report.md
    python audit_ecosystem.py --agents-dir /path/to/agents --json  # JSON output
"""

import argparse
import json
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Standard file manifests
# ──────────────────────────────────────────────────────────────────────────────

ROOT_FILES = [
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "pyproject.toml",
    "requirements.txt",
    ".pre-commit-config.yaml",
    ".bumpversion.cfg",
    ".gitignore",
    ".gitattributes",
    ".dockerignore",
    ".env",
]

DOC_FILES = ["docs/index.md", "docs/overview.md", "docs/concepts.md"]
DEPRECATED_FILES = ["docs/legacy_readme.md"]
DOCKER_FILES = ["docker/Dockerfile", "docker/mcp.compose.yml"]

SOURCE_FILES = [
    "__init__.py",
    "__main__.py",
    "agent_server.py",
    "mcp_server.py",
]

TEST_FILES = [
    "tests/conftest.py",
    "tests/test_concept_parity.py",
    "tests/test_init_dynamics.py",
    "tests/test_startup.py",
]

# Env var patterns that indicate non-standard naming
NONSTANDARD_ENV_PATTERNS = [
    (r"_BASE_URL", "_URL", "Use {SERVICE}_URL instead of _BASE_URL"),
    (r"_INSTANCE", "_URL", "Use {SERVICE}_URL instead of _INSTANCE"),
    (
        r"_AGENT_VERIFY",
        "_SSL_VERIFY",
        "Use {SERVICE}_SSL_VERIFY instead of _AGENT_VERIFY",
    ),
    (r"_API_KEY", "_TOKEN", "Use {SERVICE}_TOKEN instead of _API_KEY"),
    (r"_ACCESS_TOKEN", "_TOKEN", "Use {SERVICE}_TOKEN instead of _ACCESS_TOKEN"),
]

# First-party env vars that are exceptions to our naming rules
FIRST_PARTY_EXCEPTIONS = {
    "GITHUB_TOKEN",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_BASE_URL",
    "ANTHROPIC_API_KEY",
    "MONGODB_URI",
    "MONGODB_HOST",
    "MONGODB_PORT",
}

# Known CONCEPT prefixes (for collision detection)
KNOWN_PREFIXES = {
    "ANSIBLE": "ansible-tower-mcp",
    "ABOX": "archivebox-api",
    "ARR": "arr-mcp",
    "ATL": "atlassian-agent",
    "AU": "agent-utilities",
    "AUDIO": "audio-transcriber",
    "CMGR": "container-manager-mcp",
    "DSCI": "data-science-mcp",
    "DOCDB": "documentdb-mcp",
    "GENIUS": "genius-agent",
    "GH": "github-agent",
    "GL": "gitlab-api",
    "HASS": "home-assistant-agent",
    "JELLYFIN": "jellyfin-mcp",
    "LF": "langfuse-agent",
    "LIX": "leanix-agent",
    "LM": "listmonk-api",
    "MEAL": "mealie-mcp",
    "MDLD": "media-downloader",
    "MSFT": "microsoft-agent",
    "NC": "nextcloud-agent",
    "OC": "owncast-agent",
    "PA": "postiz-agent",
    "PLANE": "plane-agent",
    "PORT": "portainer-agent",
    "QBT": "qbittorrent-agent",
    "RM": "repository-manager",
    "SNOW": "servicenow-api",
    "SRX": "searxng-mcp",
    "SX": "scholarx",
    "SYS": "systems-manager",
    "STIRLINGPDF": "stirlingpdf-agent",
    "TUI": "agent-terminal-ui",
    "TUN": "tunnel-manager",
    "UKA": "uptime-kuma-agent",
    "VEC": "vector-mcp",
    "WEBUI": "agent-webui",
    "WGER": "wger-agent",
}


# ──────────────────────────────────────────────────────────────────────────────
# Audit functions
# ──────────────────────────────────────────────────────────────────────────────


def audit_root_files(project_dir: Path) -> dict:
    """Check root-level file presence."""
    results = {}
    for f in ROOT_FILES:
        exists = (project_dir / f).exists()
        results[f] = {"present": exists, "required": True}
    return results


def audit_docs(project_dir: Path) -> dict:
    """Check docs structure and deprecated files."""
    results = {"present": {}, "deprecated": {}}
    for f in DOC_FILES:
        results["present"][f] = (project_dir / f).exists()
    for f in DEPRECATED_FILES:
        results["deprecated"][f] = (project_dir / f).exists()
    return results


def audit_docker(project_dir: Path) -> dict:
    """Check docker files."""
    results = {}
    for f in DOCKER_FILES:
        results[f] = (project_dir / f).exists()
    return results


def audit_source_structure(project_dir: Path, pkg_name: str) -> dict:
    """Check source directory structure."""
    src_dir = project_dir / pkg_name
    results = {"files": {}, "subdirs": {}, "issues": []}

    for f in SOURCE_FILES:
        results["files"][f] = (src_dir / f).exists()

    # auth.py is required if project has API integration
    has_api = (src_dir / "api").is_dir() or (src_dir / "api_client.py").exists()
    results["files"]["auth.py"] = (src_dir / "auth.py").exists()
    results["auth_required"] = has_api

    # mcp/ subdirectory is required if mcp_server.py exists
    has_mcp_server = (src_dir / "mcp_server.py").exists()
    has_mcp_dir = (src_dir / "mcp").is_dir()
    results["subdirs"]["mcp/"] = has_mcp_dir
    results["mcp_required"] = has_mcp_server

    if has_mcp_server and not has_mcp_dir:
        results["issues"].append("mcp_server.py exists but no mcp/ subdirectory")

    # api/ subdirectory required if api_client.py exists
    has_api_client = (src_dir / "api_client.py").exists()
    has_api_dir = (src_dir / "api").is_dir()
    results["subdirs"]["api/"] = has_api_dir
    results["api_required"] = has_api_client

    if has_api_client and not has_api_dir:
        results["issues"].append("api_client.py exists but no api/ subdirectory")

    return results


def audit_tests(project_dir: Path) -> dict:
    """Check standard test files."""
    results = {}
    for f in TEST_FILES:
        results[f] = (project_dir / f).exists()
    return results


def audit_env_vars(project_dir: Path, pkg_name: str) -> dict:
    """Audit auth.py for non-standard environment variable naming."""
    auth_file = project_dir / pkg_name / "auth.py"
    results = {"standard": True, "issues": [], "vars_found": []}

    if not auth_file.exists():
        return results

    content = auth_file.read_text()
    env_vars = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
    results["vars_found"] = sorted(set(env_vars))

    for var in results["vars_found"]:
        if var in FIRST_PARTY_EXCEPTIONS:
            continue
        for pattern, standard, msg in NONSTANDARD_ENV_PATTERNS:
            if re.search(pattern, var):
                # Check if already migrated with backward-compat fallback:
                # os.getenv("NEW_VAR") or os.getenv("OLD_VAR", ...)
                new_var = re.sub(pattern, standard, var)
                if f'os.getenv("{new_var}")' in content:
                    continue  # Already migrated with backward compat
                results["issues"].append(f"`{var}`: {msg}")
                results["standard"] = False

    # Check for duplicate purpose vars (e.g., both _BASE_URL and _URL)
    # But skip if they're part of a backward-compat fallback pattern
    url_vars = [v for v in results["vars_found"] if "URL" in v or "INSTANCE" in v]
    if len(url_vars) > 1:
        # Filter out vars that appear in "or os.getenv" fallback chains
        genuine_url_vars = []
        for v in url_vars:
            # If this var only appears as a fallback (after 'or os.getenv'), skip it
            primary_pattern = re.compile(rf'(?<!or )os\.getenv\("{re.escape(v)}"')
            if primary_pattern.search(content):
                genuine_url_vars.append(v)
        if len(genuine_url_vars) > 1:
            prefixes = set()
            for v in genuine_url_vars:
                prefix = v.rsplit("_", 1)[0] if "_URL" in v or "_INSTANCE" in v else v
                prefix = prefix.replace("_BASE", "").replace("_AGENT", "")
                prefixes.add(prefix)
            if len(prefixes) < len(genuine_url_vars):
                results["issues"].append(
                    f"Potential duplicate URL vars: {genuine_url_vars}"
                )

    return results


def audit_concepts(project_dir: Path, project_name: str) -> dict:
    """Audit CONCEPT ID registry."""
    concepts_file = project_dir / "docs" / "concepts.md"
    results = {
        "has_concepts_md": concepts_file.exists(),
        "prefix": None,
        "concept_count": 0,
        "has_bridge_ref": False,
        "issues": [],
    }

    if not concepts_file.exists():
        results["issues"].append("Missing docs/concepts.md")
        return results

    content = concepts_file.read_text()

    # Extract prefix
    prefix_match = re.search(r"CONCEPT:([A-Z_]+)-", content)
    if prefix_match:
        results["prefix"] = prefix_match.group(1)

    # Count concepts
    concepts = re.findall(r"CONCEPT:[A-Z_]+-\d+", content)
    results["concept_count"] = len(set(concepts))

    # Check ECO-4.0 bridge reference
    results["has_bridge_ref"] = "ECO-4.0" in content

    if not results["has_bridge_ref"]:
        results["issues"].append("Missing ECO-4.0 bridge reference")

    # Check for collision with known prefixes
    if results["prefix"] and results["prefix"] in KNOWN_PREFIXES:
        expected = KNOWN_PREFIXES[results["prefix"]]
        if expected != project_name:
            results["issues"].append(
                f"Prefix {results['prefix']} collides with {expected}"
            )

    return results


def audit_pyproject(project_dir: Path) -> dict:
    """Audit pyproject.toml for standard fields."""
    toml_path = project_dir / "pyproject.toml"
    results = {"valid": False, "issues": [], "version": None, "name": None}

    if not toml_path.exists():
        results["issues"].append("Missing pyproject.toml")
        return results

    try:
        data = tomllib.loads(toml_path.read_text())
        results["valid"] = True
        project = data.get("project", {})
        results["name"] = project.get("name")
        results["version"] = project.get("version")

        # Check for standard fields
        if not project.get("description"):
            results["issues"].append("Missing project.description")
        if not project.get("readme"):
            results["issues"].append("Missing project.readme")
        if not project.get("requires-python"):
            results["issues"].append("Missing project.requires-python")

        # Check for circular deps (self-reference)
        deps = project.get("dependencies", [])
        name = results["name"] or ""
        for dep in deps:
            dep_name = re.split(r"[\[>=<\s]", dep)[0].lower()
            if dep_name == name.lower():
                results["issues"].append(f"Self-dependency detected: {dep}")

    except Exception as e:
        results["issues"].append(f"Parse error: {type(e).__name__}")

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────────────────────────────────────

WEIGHTS = {
    "root_files": 0.15,
    "docs": 0.15,
    "docker": 0.10,
    "source": 0.20,
    "tests": 0.15,
    "env_vars": 0.15,
    "concepts": 0.10,
}


def score_category(present: int, total: int, penalties: int = 0) -> float:
    """Score a category 0–100."""
    if total == 0:
        return 100.0
    base = (present / total) * 100
    return min(100.0, max(0, base - (penalties * 10)))


def compute_scores(audit: dict) -> dict:
    """Compute per-category and overall scores."""
    scores = {}

    # Root files
    root = audit["root_files"]
    present = sum(1 for v in root.values() if v["present"])
    scores["root_files"] = score_category(present, len(root))

    # Docs
    docs = audit["docs"]
    present = sum(1 for v in docs["present"].values() if v)
    penalties = sum(1 for v in docs["deprecated"].values() if v)
    scores["docs"] = score_category(present, len(docs["present"]), penalties)

    # Docker
    docker = audit["docker"]
    present = sum(1 for v in docker.values() if v)
    scores["docker"] = score_category(present, len(docker))

    # Source structure
    src = audit["source"]
    present = 0
    total = 0
    for f, exists in src["files"].items():
        # auth.py is only required if auth_required
        if f == "auth.py" and not src.get("auth_required", False):
            if exists:
                present += 1  # Bonus, but don't penalize absence
            continue
        total += 1
        if exists:
            present += 1
    # Add subdirs that are required
    if src["mcp_required"]:
        total += 1
        if src["subdirs"].get("mcp/"):
            present += 1
    if src["api_required"]:
        total += 1
        if src["subdirs"].get("api/"):
            present += 1
    scores["source"] = score_category(present, total, len(src["issues"]))

    # Tests
    tests = audit["tests"]
    present = sum(1 for v in tests.values() if v)
    scores["tests"] = score_category(present, len(tests))

    # Env vars
    env = audit["env_vars"]
    if not env["vars_found"]:
        scores["env_vars"] = 100.0
    else:
        scores["env_vars"] = score_category(
            max(0, len(env["vars_found"]) - len(env["issues"])),
            len(env["vars_found"]),
        )

    # Concepts
    concepts = audit["concepts"]
    concept_checks = [
        concepts["has_concepts_md"],
        concepts["has_bridge_ref"],
        concepts["concept_count"] > 0,
        len(concepts["issues"]) == 0,
    ]
    present = sum(1 for c in concept_checks if c)
    scores["concepts"] = score_category(present, len(concept_checks))

    # Weighted overall
    scores["overall"] = sum(scores[cat] * weight for cat, weight in WEIGHTS.items())

    return scores


def grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "🟢 A"
    elif score >= 75:
        return "🟡 B"
    elif score >= 60:
        return "🟠 C"
    else:
        return "🔴 D"


# ──────────────────────────────────────────────────────────────────────────────
# Report generation
# ──────────────────────────────────────────────────────────────────────────────


def audit_project(project_dir: Path) -> dict:
    """Run full audit on a single project."""
    project_name = project_dir.name
    pkg_name = project_name.replace("-", "_")

    audit = {
        "name": project_name,
        "root_files": audit_root_files(project_dir),
        "docs": audit_docs(project_dir),
        "docker": audit_docker(project_dir),
        "source": audit_source_structure(project_dir, pkg_name),
        "tests": audit_tests(project_dir),
        "env_vars": audit_env_vars(project_dir, pkg_name),
        "concepts": audit_concepts(project_dir, project_name),
        "pyproject": audit_pyproject(project_dir),
    }

    audit["scores"] = compute_scores(audit)
    return audit


def generate_markdown_report(audits: list[dict], output_path: Path | None) -> str:
    """Generate a markdown drift report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Ecosystem Drift Report",
        "",
        f"> Generated: {now}",
        f"> Projects scanned: {len(audits)}",
        "",
    ]

    # Overall summary
    avg_score = (
        sum(a["scores"]["overall"] for a in audits) / len(audits) if audits else 0
    )
    lines.extend(
        [
            f"## Overall Ecosystem Compliance: {avg_score:.1f}/100 ({grade(avg_score)})",
            "",
            "### Category Averages",
            "",
            "| Category | Average Score | Grade |",
            "|----------|-------------|-------|",
        ]
    )

    for cat in WEIGHTS:
        cat_avg = sum(a["scores"][cat] for a in audits) / len(audits) if audits else 0
        lines.append(
            f"| {cat.replace('_', ' ').title()} | {cat_avg:.1f} | {grade(cat_avg)} |"
        )

    # Per-project scorecards
    lines.extend(
        [
            "",
            "---",
            "",
            "## Per-Project Scorecards",
            "",
            "| Project | Overall | Root | Docs | Docker | Source | Tests | Env Vars | Concepts |",
            "|---------|---------|------|------|--------|--------|-------|----------|----------|",
        ]
    )

    sorted_audits = sorted(audits, key=lambda a: a["scores"]["overall"])
    for a in sorted_audits:
        s = a["scores"]
        g = grade(s["overall"])
        line = f"| {a['name']} | {g} {s['overall']:.0f} |"
        for cat in WEIGHTS:
            line += f" {s[cat]:.0f} |"
        lines.append(line)

    # Drift details (only for projects below 100)
    lines.extend(["", "---", "", "## Drift Details", ""])

    for a in sorted_audits:
        if a["scores"]["overall"] >= 99.5:
            continue  # Skip fully compliant

        lines.append(
            f"### {a['name']} — {grade(a['scores']['overall'])} ({a['scores']['overall']:.0f}/100)"
        )
        lines.append("")

        issues = []

        # Root file issues
        for f, v in a["root_files"].items():
            if not v["present"]:
                issues.append(f"❌ Missing `{f}`")

        # Doc issues
        for f, present in a["docs"]["present"].items():
            if not present:
                issues.append(f"❌ Missing `{f}`")
        for f, present in a["docs"]["deprecated"].items():
            if present:
                issues.append(f"⚠️ Deprecated `{f}` still exists — remove it")

        # Docker issues
        for f, present in a["docker"].items():
            if not present:
                issues.append(f"❌ Missing `{f}`")

        # Source issues
        for f, present in a["source"]["files"].items():
            if not present:
                # auth.py is only required when auth_required
                if f == "auth.py" and not a["source"].get("auth_required", False):
                    continue
                issues.append(f"❌ Missing `{{pkg}}/{f}`")
        for issue in a["source"]["issues"]:
            issues.append(f"⚠️ {issue}")

        # Test issues
        for f, present in a["tests"].items():
            if not present:
                issues.append(f"❌ Missing `{f}`")

        # Env var issues
        for issue in a["env_vars"]["issues"]:
            issues.append(f"⚠️ Env var: {issue}")

        # Concept issues
        for issue in a["concepts"]["issues"]:
            issues.append(f"❌ Concept: {issue}")

        # Pyproject issues
        for issue in a["pyproject"]["issues"]:
            issues.append(f"⚠️ pyproject: {issue}")

        if issues:
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- ✅ No specific issues detected")
        lines.append("")

    # CONCEPT ID collision check
    lines.extend(["---", "", "## CONCEPT ID Collision Check", ""])
    prefixes_found = {}
    for a in audits:
        prefix = a["concepts"].get("prefix")
        if prefix:
            prefixes_found.setdefault(prefix, []).append(a["name"])

    collisions = {p: names for p, names in prefixes_found.items() if len(names) > 1}
    if collisions:
        lines.append("⚠️ **Collisions detected:**")
        for prefix, names in collisions.items():
            lines.append(f"- `{prefix}`: {', '.join(names)}")
    else:
        lines.append(f"✅ No collisions across {len(prefixes_found)} prefixes")

    lines.append("")
    report = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        print(f"📄 Report written to {output_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Ecosystem drift audit")
    parser.add_argument(
        "--agents-dir", default="agent-packages/agents", help="Path to agents directory"
    )
    parser.add_argument("--output", default=None, help="Output markdown report path")
    parser.add_argument(
        "--json", action="store_true", help="Output JSON instead of markdown"
    )
    parser.add_argument(
        "--projects", default=None, help="Comma-separated list of specific projects"
    )
    args = parser.parse_args()

    agents_dir = Path(args.agents_dir)
    if not agents_dir.exists():
        print("❌ Configured agents directory was not found")
        sys.exit(1)

    # Discover projects
    if args.projects:
        projects = [agents_dir / p.strip() for p in args.projects.split(",")]
    else:
        projects = sorted(
            d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        )

    print(f"🔍 Auditing {len(projects)} projects...")
    audits = []
    for project_dir in projects:
        if not project_dir.exists():
            print("  ⚠️ Skipping configured project (not found)")
            continue
        audit = audit_project(project_dir)
        g = grade(audit["scores"]["overall"])
        print(f"  {g} {project_dir.name}: {audit['scores']['overall']:.0f}/100")
        audits.append(audit)

    if args.json:
        output = json.dumps(audits, indent=2, default=str)
        if args.output:
            Path(args.output).write_text(output)
        else:
            print(output)
    else:
        output_path = Path(args.output) if args.output else None
        report = generate_markdown_report(audits, output_path)
        if not output_path:
            print(report)

    # Summary
    avg = sum(a["scores"]["overall"] for a in audits) / len(audits) if audits else 0
    print(f"\n📊 Ecosystem compliance: {avg:.1f}/100 ({grade(avg)})")
    below_90 = [a for a in audits if a["scores"]["overall"] < 90]
    if below_90:
        print(f"   {len(below_90)} projects below 90% compliance")


if __name__ == "__main__":
    main()
