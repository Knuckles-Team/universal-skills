#!/usr/bin/env python3
"""FR-014: SDD handoff generator for code-enhancer skill.

Produces structured TODO items compatible with spec-generator -> task-planner
-> sdd-implementer pipeline. Outputs both JSON and Markdown to .specify/specs/.

CONCEPT:CE-014 — SDD Handoff
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _priority_from_grade(grade: str) -> str:
    return {"F": "P0-Critical", "D": "P1-High", "C": "P2-Medium", "B": "P3-Low", "A": "P4-Enhancement"}.get(grade, "P2-Medium")


def _effort_estimate(finding: str) -> str:
    length = len(finding)
    if length > 80:
        return "Large"
    if length > 40:
        return "Medium"
    return "Small"


def generate_sdd_handoff(results: list[dict], project_name: str = "Unknown",
                         output_dir: str | None = None) -> dict:
    """Generate SDD-compatible handoff from enhancement results.

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

    # Build tasks
    tasks: list[dict] = []
    task_id = 0

    for r in results:
        domain = r.get("domain", "Unknown")
        grade = r.get("grade", "F")
        score = r.get("score", 0)
        priority = _priority_from_grade(grade)

        # Add user story
        spec["user_stories"].append({
            "role": "developer",
            "action": f"address {domain} findings (grade: {grade}, score: {score})",
            "value": f"improve project {domain.lower()} from {grade} to at least B (80+)",
        })

        for finding in r.get("findings", []):
            task_id += 1
            task = {
                "id": f"T{task_id:03d}",
                "title": f"[{domain}] {finding[:60]}",
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

            spec["functional_requirements"].append({
                "id": f"FR-{task_id:03d}",
                "description": finding,
                "testable": True,
            })

    # Success criteria
    overall_gpa = sum({"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(r.get("grade", "F"), 0)
                       for r in results) / max(len(results), 1)
    spec["success_criteria"] = [
        {"metric": "Overall GPA", "current": round(overall_gpa, 2), "target": 3.0},
        {"metric": "Domains at B or above", "current": sum(1 for r in results if r.get("grade") in ("A", "B")),
         "target": len(results)},
        {"metric": "Critical findings resolved", "current": 0,
         "target": sum(1 for t in tasks if t["priority"] == "P0-Critical")},
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
        },
    }

    # Write to .specify/ if output_dir given
    if output_dir:
        out_root = Path(output_dir)
        spec_dir = out_root / ".specify" / "specs" / feature_id
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Write spec.json
        (spec_dir / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")

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
            spec_md_lines.append(f"- As a **{us['role']}**, I want to **{us['action']}**, so that **{us['value']}**.")
        spec_md_lines.extend(["", "## Functional Requirements", ""])
        for fr in spec["functional_requirements"]:
            spec_md_lines.append(f"- **{fr['id']}**: {fr['description']}")
        spec_md_lines.extend(["", "## Success Criteria", ""])
        for sc in spec["success_criteria"]:
            spec_md_lines.append(f"- {sc['metric']}: {sc['current']} → {sc['target']}")

        (spec_dir / "spec.md").write_text("\n".join(spec_md_lines), encoding="utf-8")

        # Write tasks.json
        (spec_dir / "tasks.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")

        # Write tasks.md
        tasks_md_lines = [f"# Tasks: {spec['title']}", "",
                          f"Generated: {timestamp}", ""]
        for t in tasks:
            parallel = "[P] " if not t["dependencies"] else ""
            tasks_md_lines.append(f"- [ ] {parallel}**{t['id']}** {t['title']}")
            tasks_md_lines.append(f"  - Priority: {t['priority']} | Effort: {t['effort']}")
        (spec_dir / "tasks.md").write_text("\n".join(tasks_md_lines), encoding="utf-8")

    return handoff


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate SDD handoff from enhancement results")
    parser.add_argument("results_file", help="JSON file with domain results")
    parser.add_argument("--output-dir", "-o", help="Project root for .specify/ output", default=None)
    parser.add_argument("--name", "-n", help="Project name", default="Unknown")
    args = parser.parse_args()

    with open(args.results_file) as f:
        results = json.load(f)

    handoff = generate_sdd_handoff(results, project_name=args.name, output_dir=args.output_dir)
    print(json.dumps(handoff, indent=2))
