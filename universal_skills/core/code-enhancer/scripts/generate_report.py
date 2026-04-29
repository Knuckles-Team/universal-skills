#!/usr/bin/env python3
"""FR-012, FR-013: Consolidated report generator for code-enhancer skill.

Aggregates all domain results into a prettified Markdown report with
standardized 0-100 grading, Mermaid charts, tables, and prioritized TODOs.

CONCEPT:CE-012 — Actionable Reporting
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _grade_emoji(grade: str) -> str:
    return {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}.get(grade, "⚪")


def _score_bar(score: int) -> str:
    filled = score // 5
    empty = 20 - filled
    return f"`{'█' * filled}{'░' * empty}` {score}/100"


def _compute_gpa(results: list[dict]) -> float:
    grade_points = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    if not results:
        return 0.0
    total = sum(grade_points.get(r.get("grade", "F"), 0.0) for r in results)
    return round(total / len(results), 2)


def _generate_radar_mermaid(results: list[dict]) -> str:
    """Generate a Mermaid radar-style visualization (using bar chart as proxy)."""
    lines = ["```mermaid", "xychart-beta", '    title "Domain Scores"',
             "    x-axis [" + ", ".join(f'"{r["domain"][:12]}"' for r in results) + "]",
             '    y-axis "Score" 0 --> 100',
             "    bar [" + ", ".join(str(r.get("score", 0)) for r in results) + "]",
             "```"]
    return "\n".join(lines)


def _generate_traffic_light(results: list[dict]) -> str:
    """Generate traffic-light summary table."""
    lines = ["| Domain | Grade | Score | Status |",
             "|--------|-------|-------|--------|"]
    for r in sorted(results, key=lambda x: x.get("score", 0)):
        emoji = _grade_emoji(r.get("grade", "F"))
        lines.append(f"| {r['domain']} | {emoji} {r.get('grade', 'F')} | "
                     f"{r.get('score', 0)}/100 | {_score_bar(r.get('score', 0))} |")
    return "\n".join(lines)


def _generate_todo_section(results: list[dict]) -> str:
    """Generate prioritized TODO section from all findings."""
    todos: list[dict] = []
    priority_order = {"F": 0, "D": 1, "C": 2, "B": 3, "A": 4}

    for r in results:
        grade = r.get("grade", "F")
        domain = r.get("domain", "Unknown")
        for finding in r.get("findings", []):
            impact = "High" if grade in ("F", "D") else "Medium" if grade == "C" else "Low"
            risk = "High" if grade == "F" else "Medium" if grade == "D" else "Low"
            todos.append({
                "domain": domain,
                "finding": finding,
                "impact": impact,
                "risk": risk,
                "priority": priority_order.get(grade, 5),
                "grade": grade,
            })

    todos.sort(key=lambda x: x["priority"])

    lines = ["| # | Priority | Domain | Action | Impact | Risk |",
             "|---|----------|--------|--------|--------|------|"]
    for i, todo in enumerate(todos[:30], 1):
        priority_emoji = "🔴" if todo["impact"] == "High" else "🟡" if todo["impact"] == "Medium" else "🟢"
        lines.append(f"| {i} | {priority_emoji} {todo['impact']} | {todo['domain']} | "
                     f"{todo['finding'][:80]} | {todo['impact']} | {todo['risk']} |")

    return "\n".join(lines)


def _generate_domain_scorecard(result: dict) -> str:
    """Generate a detailed scorecard for a single domain."""
    grade = result.get("grade", "F")
    score = result.get("score", 0)
    domain = result.get("domain", "Unknown")
    emoji = _grade_emoji(grade)

    alert_type = "CAUTION" if grade == "F" else "WARNING" if grade == "D" else "NOTE" if grade in ("B", "C") else "TIP"

    lines = [
        f"### {domain} — {emoji} Grade: {grade} ({score}/100)",
        "",
        _score_bar(score),
        "",
    ]

    # Summary alert
    summary = result.get("findings", ["No findings"])
    if summary:
        lines.extend([f"> [!{alert_type}]", f"> {summary[0]}", ""])

    # Justification table
    justifications = result.get("justifications", [])
    if justifications:
        lines.extend(["| Criterion | Points | Evidence | Reasoning |",
                       "|-----------|--------|----------|-----------|"])
        for j in justifications:
            evidence = str(j.get("evidence", ""))[:60]
            reasoning = str(j.get("reasoning", ""))[:80]
            lines.append(f"| {j.get('criterion', '')} | {j.get('points', 0)} | "
                         f"`{evidence}` | {reasoning} |")
        lines.append("")

    # Detailed findings
    if len(summary) > 1:
        lines.append("**Findings:**")
        for f in summary[1:5]:
            lines.append(f"- {f}")
        lines.append("")

    return "\n".join(lines)


def generate_report(results: list[dict], project_name: str = "Unknown",
                    output_path: str | None = None) -> str:
    """Generate the full prettified report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    gpa = _compute_gpa(results)

    sections = [
        f"# 🔬 Code Enhancement Report",
        "",
        f"> **Generated**: {timestamp} | **Target**: {project_name} | **Overall GPA**: {gpa}/4.0",
        "",
        "---",
        "",
        "## 📊 Executive Summary",
        "",
        _generate_radar_mermaid(results),
        "",
        _generate_traffic_light(results),
        "",
        "---",
        "",
        "## 📋 Domain Scorecards",
        "",
    ]

    for r in results:
        sections.append(_generate_domain_scorecard(r))
        sections.append("---\n")

    sections.extend([
        "## 🎯 Prioritized Action Items",
        "",
        _generate_todo_section(results),
        "",
        "---",
        "",
        "## 🔄 SDD Handoff",
        "",
        "Run `generate_sdd_handoff.py` with this report's JSON data to produce",
        "structured TODO items compatible with the `spec-generator` → `task-planner` →",
        "`sdd-implementer` pipeline. Output will be saved to `.specify/specs/`.",
        "",
    ])

    report = "\n".join(sections)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")

    return report


if __name__ == "__main__":
    # Accept a JSON file with all domain results
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <results.json> [--output path] [--name project_name]")
        print("\nThe results.json should be a JSON array of domain result objects.")
        print("Each object should have: domain, score, grade, findings, justifications")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="Generate code enhancement report")
    parser.add_argument("results_file", help="JSON file with domain results")
    parser.add_argument("--output", "-o", help="Output path for report", default=None)
    parser.add_argument("--name", "-n", help="Project name", default="Unknown")
    args = parser.parse_args()

    with open(args.results_file) as f:
        results = json.load(f)

    report = generate_report(results, project_name=args.name, output_path=args.output)
    if not args.output:
        print(report)
