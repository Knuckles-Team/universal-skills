#!/usr/bin/env python3
"""FR-014: SDD handoff generator for code-enhancer skill.

Produces structured TODO items compatible with spec-generator -> task-planner
-> sdd-implementer pipeline. Outputs both JSON and Markdown to .specify/specs/.

CONCEPT:CE-014 — SDD Handoff
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def _priority_from_domain_and_finding(domain: str, grade: str, finding: str) -> str:
    """Assign priority based on domain context and finding severity.

    ACCURACY FIX: The old logic assigned P0-Critical to everything from
    an F-graded domain. A minor dep bump in an F-grade domain is NOT critical.

    Rules:
        Security HIGH → P1-High
        Security MEDIUM → P2-Medium
        MAJOR dep update → P2-Medium
        Minor dep update → P3-Low
        Monolithic/refactoring → P2-Medium
        Lint findings → P2-Medium
        Concept markers → P4-Enhancement
        All else → domain grade mapping
    """
    finding_lower = finding.lower()

    # Security findings use severity from the finding text
    if "security" in domain.lower():
        if "high" in finding_lower:
            return "P1-High"
        if "medium" in finding_lower:
            return "P2-Medium"
        if "low" in finding_lower:
            return "P3-Low"
        if "eval" in finding_lower or "exec" in finding_lower:
            return "P2-Medium"
        return "P2-Medium"

    # Dependency findings use update type
    if "dependency" in domain.lower() or "audit" in domain.lower():
        if "major" in finding_lower:
            return "P2-Medium"
        if "minor" in finding_lower:
            return "P3-Low"
        if "patch" in finding_lower:
            return "P4-Enhancement"
        return "P3-Low"

    # Architecture/codebase findings
    if "codebase" in domain.lower() or "architecture" in domain.lower():
        if "monolithic" in finding_lower or ">1000" in finding_lower:
            return "P1-High"
        if "exceed" in finding_lower or "nesting" in finding_lower:
            return "P2-Medium"
        return "P2-Medium"

    # Concept traceability is always enhancement
    if "concept" in domain.lower() or "traceability" in domain.lower():
        return "P4-Enhancement"

    # Pre-commit is low priority
    if "pre-commit" in domain.lower():
        if "outdated" in finding_lower:
            return "P2-Medium"
        return "P3-Low"

    # Default: map from grade but never P0-Critical from automated findings
    return {
        "F": "P1-High",
        "D": "P2-Medium",
        "C": "P2-Medium",
        "B": "P3-Low",
        "A": "P4-Enhancement",
    }.get(grade, "P2-Medium")


def _effort_estimate(finding: str) -> str:
    """Estimate effort based on finding content keywords.

    ACCURACY FIX: Old logic used string length as a proxy for effort.
    Now uses keyword-based classification.
    """
    finding_lower = finding.lower()
    # Large effort: structural changes
    if any(
        w in finding_lower
        for w in [
            "monolithic",
            "split",
            "refactor",
            "reorganiz",
            ">1000",
            "god module",
            "package",
        ]
    ):
        return "Large"
    # Small effort: config, install, update
    if any(
        w in finding_lower
        for w in ["install", "update", "bump", "hook", "not available", "missing"]
    ):
        return "Small"
    return "Medium"


def _is_informational(domain: str, finding: str) -> bool:
    """Detect findings that are informational, not actionable.

    ACCURACY FIX: Ecosystem markers, positive results, and detection-only
    findings should not generate tasks.
    """
    finding_lower = finding.lower()

    # Project analysis ecosystem markers
    if "project analysis" in domain.lower():
        if any(
            w in finding_lower
            for w in [
                "detected ecosystem",
                "externalized prompts",
                "observability",
                "protocol support",
                "detected marker",
            ]
        ):
            return True

    # Positive findings (things that are working)
    if any(
        w in finding_lower
        for w in [
            "all version",
            "correctly",
            "up-to-date",
            "no issues",
            "all checks passed",
            "tracked correctly",
        ]
    ):
        return True

    # Pre-commit expected behavior
    if "pre-commit" in domain.lower():
        if "don't commit to branch" in finding_lower:
            return True
        if "skipped" in finding_lower and "handled by" in finding_lower:
            return True

    # Test execution — "no tests found" vs "tests exist but failed"
    # is better handled by checking test collection, but we flag the
    # misleading pattern here
    if "test execution" in domain.lower():
        if "no tests were executed" in finding_lower:
            # This is often a misleading finding — tests may exist but
            # failed to collect due to missing deps. Flag as informational
            # since analyze_tests.py already counts test functions.
            return True

    return False


def generate_sdd_handoff(
    results: list[dict], project_name: str = "Unknown", output_dir: str | None = None
) -> dict:
    """Generate SDD-compatible handoff from enhancement results.

    IMPORTANT: output_dir should be the individual project root, NOT the
    monorepo root. Each project gets its own .specify/ folder so that
    SDD tasks are addressed in the correct project context.

    Example:
        - Correct:  output_dir="agent-packages/agents/github-agent"
        - Wrong:    output_dir="agent-packages"  (monorepo root)

    Returns:
        dict with spec and tasks data, also writes to .specify/ if output_dir given.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    feature_id = f"code-enhancement-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    # Build spec
    spec = {
        "feature_id": feature_id,
        "title": f"Code Enhancement: {project_name}",
        "created": timestamp,
        "overview": f"Automated code enhancement review for {project_name}. "
        f"Covers {len(results)} analysis domains.",
        "user_stories": [],
        "functional_requirements": [],
        "success_criteria": [],
    }

    # Build tasks — FILTER informational findings
    tasks: list[dict] = []
    task_id = 0
    skipped_informational = 0

    for r in results:
        domain = r.get("domain", "Unknown")
        grade = r.get("grade", "F")
        score = r.get("score", 0)

        # Add user story (only if grade < B — don't create stories for passing domains)
        if grade not in ("A", "B"):
            spec["user_stories"].append(
                {
                    "role": "developer",
                    "action": f"address {domain} findings (grade: {grade}, score: {score})",
                    "value": f"improve project {domain.lower()} from {grade} to at least B (80+)",
                }
            )

        for finding in r.get("findings", []):
            # ACCURACY FIX: Skip informational findings
            if _is_informational(domain, finding):
                skipped_informational += 1
                continue

            task_id += 1
            priority = _priority_from_domain_and_finding(domain, grade, finding)
            task = {
                "id": f"T{task_id:03d}",
                "title": f"[{domain}] {finding[:80]}",
                "description": finding,
                "domain": domain,
                "priority": priority,
                "effort": _effort_estimate(finding),
                "status": "PENDING",
                "dependencies": [],
                "file_paths": [],
                "grade_before": grade,
                "score_before": score,
            }
            tasks.append(task)

            spec["functional_requirements"].append(
                {
                    "id": f"FR-{task_id:03d}",
                    "description": finding,
                    "testable": True,
                }
            )

    # Success criteria
    overall_gpa = sum(
        {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(r.get("grade", "F"), 0)
        for r in results
    ) / max(len(results), 1)
    spec["success_criteria"] = [
        {"metric": "Overall GPA", "current": round(overall_gpa, 2), "target": 3.0},
        {
            "metric": "Domains at B or above",
            "current": sum(1 for r in results if r.get("grade") in ("A", "B")),
            "target": len(results),
        },
        {"metric": "Actionable findings", "current": len(tasks), "target": 0},
    ]

    handoff = {
        "feature_id": feature_id,
        "spec": spec,
        "tasks": tasks,
        "metadata": {
            "generated_by": "code-enhancer",
            "timestamp": timestamp,
            "project": project_name,
            "domain_count": len(results),
            "task_count": len(tasks),
            "skipped_informational": skipped_informational,
        },
    }

    # Write to .specify/ if output_dir given
    if output_dir:
        out_root = Path(output_dir)
        spec_dir = out_root / ".specify" / "specs" / feature_id
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Write spec.json
        (spec_dir / "spec.json").write_text(
            json.dumps(spec, indent=2), encoding="utf-8"
        )

        # Write spec.md
        spec_md_lines = [
            f"# {spec['title']}",
            "",
            f"> {spec['overview']}",
            "",
            "## User Stories",
            "",
        ]
        for us in spec["user_stories"]:
            spec_md_lines.append(
                f"- As a **{us['role']}**, I want to **{us['action']}**, so that **{us['value']}**."
            )
        spec_md_lines.extend(["", "## Functional Requirements", ""])
        for fr in spec["functional_requirements"]:
            spec_md_lines.append(f"- **{fr['id']}**: {fr['description']}")
        spec_md_lines.extend(["", "## Success Criteria", ""])
        for sc in spec["success_criteria"]:
            spec_md_lines.append(f"- {sc['metric']}: {sc['current']} → {sc['target']}")

        (spec_dir / "spec.md").write_text("\n".join(spec_md_lines), encoding="utf-8")

        # Write tasks.json
        (spec_dir / "tasks.json").write_text(
            json.dumps(tasks, indent=2), encoding="utf-8"
        )

        # Write tasks.md
        tasks_md_lines = [
            f"# Tasks: {spec['title']}",
            "",
            f"Generated: {timestamp}",
            f"Skipped informational: {skipped_informational}",
            "",
        ]
        for t in tasks:
            parallel = "[P] " if not t["dependencies"] else ""
            tasks_md_lines.append(f"- [ ] {parallel}**{t['id']}** {t['title']}")
            tasks_md_lines.append(
                f"  - Priority: {t['priority']} | Effort: {t['effort']}"
            )
        (spec_dir / "tasks.md").write_text("\n".join(tasks_md_lines), encoding="utf-8")

    return handoff


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate SDD handoff from enhancement results"
    )
    parser.add_argument("results_file", help="JSON file with domain results")
    parser.add_argument(
        "--output-dir", "-o", help="Project root for .specify/ output", default=None
    )
    parser.add_argument("--name", "-n", help="Project name", default="Unknown")
    args = parser.parse_args()

    with open(args.results_file) as f:
        results = json.load(f)

    handoff = generate_sdd_handoff(
        results, project_name=args.name, output_dir=args.output_dir
    )
    print(json.dumps(handoff, indent=2))
