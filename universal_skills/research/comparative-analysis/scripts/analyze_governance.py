#!/usr/bin/env python3
"""CA-001: Governance analysis — License, ownership, contributors, bus factor.

Usage: python analyze_governance.py /path/to/project

CONCEPT:CA-001 — Project Identity & Governance
"""

import json
import re
import subprocess
import sys
from pathlib import Path

LICENSE_SPDX = {
    "MIT": {"spdx": "MIT", "osi": True, "tier": "green"},
    "Apache": {"spdx": "Apache-2.0", "osi": True, "tier": "green"},
    "BSD": {"spdx": "BSD-3-Clause", "osi": True, "tier": "green"},
    "ISC": {"spdx": "ISC", "osi": True, "tier": "green"},
    "GPL": {"spdx": "GPL-3.0-only", "osi": True, "tier": "red"},
    "LGPL": {"spdx": "LGPL-3.0-only", "osi": True, "tier": "yellow"},
    "AGPL": {"spdx": "AGPL-3.0-only", "osi": True, "tier": "red"},
    "MPL": {"spdx": "MPL-2.0", "osi": True, "tier": "yellow"},
    "Unlicense": {"spdx": "Unlicense", "osi": True, "tier": "green"},
}

GOVERNANCE_FILES = [
    "GOVERNANCE.md",
    "MAINTAINERS.md",
    "CODEOWNERS",
    ".github/CODEOWNERS",
    "CODE_OF_CONDUCT.md",
    ".github/CODE_OF_CONDUCT.md",
    "SECURITY.md",
    ".github/SECURITY.md",
    "CONTRIBUTING.md",
    ".github/CONTRIBUTING.md",
    "CLA.md",
]


def detect_license(project_path: Path) -> dict:
    """Detect license type from LICENSE file content."""
    for name in ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENCE"]:
        lpath = project_path / name
        if lpath.exists():
            try:
                content = lpath.read_text(errors="ignore")[:2000].upper()
                for key, info in LICENSE_SPDX.items():
                    if key.upper() in content:
                        return {"file": name, "detected": key, **info}
                return {
                    "file": name,
                    "detected": "unknown",
                    "spdx": "NOASSERTION",
                    "osi": False,
                    "tier": "black",
                }
            except Exception:
                pass
    return {
        "file": None,
        "detected": "none",
        "spdx": "NONE",
        "osi": False,
        "tier": "black",
    }


def analyze_contributors(project_path: Path) -> dict:
    """Analyze contributor diversity and bus factor via git log."""
    try:
        result = subprocess.run(
            ["git", "shortlog", "-sn", "--all", "--no-merges"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return {"total": 0, "bus_factor": 0, "error": "not a git repo"}
        lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        contributors = []
        for line in lines:
            match = re.match(r"(\d+)\s+(.+)", line)
            if match:
                contributors.append(
                    {"commits": int(match.group(1)), "name": match.group(2)}
                )
        total_commits = sum(c["commits"] for c in contributors)
        # Bus factor: minimum contributors covering 50% of commits
        bus_factor = 0
        cumulative = 0
        for c in sorted(contributors, key=lambda x: -x["commits"]):
            cumulative += c["commits"]
            bus_factor += 1
            if cumulative >= total_commits * 0.5:
                break
        return {
            "total": len(contributors),
            "bus_factor": bus_factor,
            "top_contributors": contributors[:5],
            "total_commits": total_commits,
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"total": 0, "bus_factor": 0, "error": "git not available"}


def check_governance_files(project_path: Path) -> dict:
    """Check presence of governance-related files."""
    found = {}
    for gf in GOVERNANCE_FILES:
        found[gf] = (project_path / gf).exists()
    return found


def score_governance(license_info: dict, contributors: dict, gov_files: dict) -> dict:
    """Calculate 0-100 governance score."""
    score = 0
    details = []

    # License (30 points max)
    tier = license_info.get("tier", "black")
    if tier == "green":
        score += 30
        details.append(f"Green license ({license_info['detected']}): +30")
    elif tier == "yellow":
        score += 20
        details.append(f"Yellow license ({license_info['detected']}): +20")
    elif tier == "red":
        score += 10
        details.append(f"Red/copyleft license ({license_info['detected']}): +10")
    else:
        details.append("No license or unrecognized: +0")

    if license_info.get("file"):
        score += 5
        details.append("LICENSE file present: +5")

    # Contributors (30 points max)
    total = contributors.get("total", 0)
    bus = contributors.get("bus_factor", 0)
    if total >= 10:
        score += 15
        details.append(f"10+ contributors ({total}): +15")
    elif total >= 5:
        score += 10
        details.append(f"5+ contributors ({total}): +10")
    elif total >= 2:
        score += 5
        details.append(f"2+ contributors ({total}): +5")

    if bus >= 3:
        score += 15
        details.append(f"Bus factor >= 3 ({bus}): +15")
    elif bus >= 2:
        score += 10
        details.append(f"Bus factor 2 ({bus}): +10")
    elif bus >= 1:
        score += 5
        details.append(f"Bus factor 1 ({bus}): +5")

    # Governance files (35 points max)
    gov_scoring = {
        "CODE_OF_CONDUCT.md": 10,
        ".github/CODE_OF_CONDUCT.md": 10,
        "CONTRIBUTING.md": 10,
        ".github/CONTRIBUTING.md": 10,
        "SECURITY.md": 5,
        ".github/SECURITY.md": 5,
        "CODEOWNERS": 5,
        ".github/CODEOWNERS": 5,
        "GOVERNANCE.md": 5,
    }
    awarded = set()
    for gf, present in gov_files.items():
        if present and gf in gov_scoring:
            base = gf.split("/")[-1]
            if base not in awarded:
                score += gov_scoring[gf]
                details.append(f"{gf} present: +{gov_scoring[gf]}")
                awarded.add(base)

    return {"score": min(score, 100), "grade": _grade(score), "details": details}


def _grade(score: int) -> str:
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 85:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 75:
        return "C+"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_governance.py <project_path>"}))
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    if not project_path.exists():
        print(json.dumps({"error": f"Path does not exist: {project_path}"}))
        sys.exit(1)

    license_info = detect_license(project_path)
    contributors = analyze_contributors(project_path)
    gov_files = check_governance_files(project_path)
    scoring = score_governance(license_info, contributors, gov_files)

    output = {
        "domain": "CA-001",
        "domain_name": "Governance",
        "project": str(project_path),
        "license": license_info,
        "contributors": contributors,
        "governance_files": gov_files,
        "scoring": scoring,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
