#!/usr/bin/env python3
"""CA-009: Generate unified comparison report from individual domain results.

Consumes JSON results from all domain analyzers and produces a structured
Markdown comparison report with radar charts, winner matrices, and
recommendations.

Usage:
    python generate_comparison_report.py result1.json result2.json [...]
    python generate_comparison_report.py --results-dir /path/to/results/
    python generate_comparison_report.py --output /path/to/report.md result1.json

CONCEPT:CA-009 — Comparative Report Generation
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DOMAIN_WEIGHTS = {
    "CA-001": 0.08,
    "CA-002": 0.10,
    "CA-003": 0.18,
    "CA-004": 0.15,
    "CA-005": 0.15,
    "CA-006": 0.12,
    "CA-007": 0.12,
    "CA-008": 0.10,
}

DOMAIN_NAMES = {
    "CA-001": "Governance",
    "CA-002": "Ecosystem Health",
    "CA-003": "Architecture",
    "CA-004": "Code Quality",
    "CA-005": "Security",
    "CA-006": "Testing",
    "CA-007": "Documentation",
    "CA-008": "Performance",
}

DOMAIN_SHORT = {
    "CA-001": "Gov",
    "CA-002": "Health",
    "CA-003": "Arch",
    "CA-004": "Quality",
    "CA-005": "Security",
    "CA-006": "Test",
    "CA-007": "Docs",
    "CA-008": "Perf",
}


def load_results(paths: list[str]) -> dict[str, dict[str, dict]]:
    """Load and organize results by project and domain."""
    projects: dict[str, dict[str, dict]] = {}

    for path_str in paths:
        path = Path(path_str)
        if path.is_dir():
            files = sorted(path.glob("*.json"))
        else:
            files = [path]

        for f in files:
            try:
                data = json.loads(f.read_text())
                project = Path(data.get("project", "unknown")).name
                domain = data.get("domain", "unknown")
                if project not in projects:
                    projects[project] = {}
                projects[project][domain] = data
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)

    return projects


def compute_gpa(domain_scores: dict[str, float]) -> float:
    """Compute weighted GPA from domain scores."""
    total_weight = 0
    weighted_sum = 0
    for domain, weight in DOMAIN_WEIGHTS.items():
        if domain in domain_scores:
            weighted_sum += domain_scores[domain] * weight
            total_weight += weight
    return round(weighted_sum / max(total_weight, 0.01), 1)


def determine_winners(projects: dict[str, dict[str, dict]]) -> dict[str, dict]:
    """Determine winner per domain."""
    winners = {}
    for domain in DOMAIN_NAMES:
        scores = {}
        for project, domains in projects.items():
            if domain in domains:
                score = domains[domain].get("scoring", {}).get("score", 0)
                scores[project] = score
        if scores:
            winner = max(scores, key=scores.get)
            sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
            delta = (
                sorted_scores[0][1] - sorted_scores[1][1]
                if len(sorted_scores) > 1
                else 0
            )
            winners[domain] = {
                "winner": winner,
                "score": scores[winner],
                "delta": delta,
                "all_scores": scores,
            }
    return winners


def generate_radar_chart(projects: dict[str, dict[str, dict]]) -> str:
    """Generate Mermaid radar chart syntax."""
    labels = list(DOMAIN_SHORT.values())
    lines = [
        "```mermaid",
        "%%{init: {'theme': 'dark'}}%%",
        "radar-beta",
        "  title Comparative Analysis Radar",
        f"  axis {', '.join(labels)}",
    ]
    for project, domains in projects.items():
        scores = []
        for domain_id in DOMAIN_SHORT:
            score = domains.get(domain_id, {}).get("scoring", {}).get("score", 0)
            scores.append(str(score))
        lines.append(f'  "{project}" : [{", ".join(scores)}]')
    lines.append("```")
    return "\n".join(lines)


def generate_report(
    projects: dict[str, dict[str, dict]], output_path: str | None
) -> str:
    """Generate the full comparison report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    project_names = list(projects.keys())

    # Compute GPAs
    gpas = {}
    for project, domains in projects.items():
        domain_scores = {}
        for domain_id in DOMAIN_NAMES:
            if domain_id in domains:
                domain_scores[domain_id] = (
                    domains[domain_id].get("scoring", {}).get("score", 0)
                )
        gpas[project] = compute_gpa(domain_scores)

    winners = determine_winners(projects)

    # Build report
    report = []
    report.append(f"# Comparative Analysis Report")
    report.append(f"\n**Date**: {now}")
    report.append(f"**Projects Analyzed**: {len(project_names)}")
    report.append(f"**Projects**: {', '.join(project_names)}")

    # Executive Summary
    report.append("\n## Executive Summary\n")
    overall_winner = max(gpas, key=gpas.get) if gpas else "N/A"
    report.append(
        f"**Overall Leader**: **{overall_winner}** (GPA: {gpas.get(overall_winner, 0)})"
    )
    for proj, gpa in sorted(gpas.items(), key=lambda x: -x[1]):
        report.append(f"- {proj}: **{gpa}**/100 weighted GPA")

    # Comparison Matrix
    report.append("\n## Comparison Matrix\n")
    header = (
        "| Domain |" + " | ".join(f"**{p}**" for p in project_names) + " | Winner |"
    )
    sep = "|--------|" + " | ".join("---" for _ in project_names) + " | ------ |"
    report.append(header)
    report.append(sep)

    for domain_id, domain_name in DOMAIN_NAMES.items():
        scores = []
        for p in project_names:
            s = projects[p].get(domain_id, {}).get("scoring", {}).get("score", "—")
            g = projects[p].get(domain_id, {}).get("scoring", {}).get("grade", "—")
            scores.append(f"{s} ({g})")
        winner_info = winners.get(domain_id, {})
        winner_name = winner_info.get("winner", "—")
        row = f"| {domain_name} | " + " | ".join(scores) + f" | {winner_name} |"
        report.append(row)

    gpa_row = (
        "| **Weighted GPA** |"
        + " | ".join(f"**{gpas.get(p, 0)}**" for p in project_names)
        + f" | **{overall_winner}** |"
    )
    report.append(gpa_row)

    # Radar Chart
    report.append("\n## Visual Comparison\n")
    report.append(generate_radar_chart(projects))

    # Per-Domain Deep Dives
    report.append("\n## Domain Deep Dives\n")
    for domain_id, domain_name in DOMAIN_NAMES.items():
        report.append(f"### {domain_id}: {domain_name}\n")
        winner_info = winners.get(domain_id, {})
        if winner_info:
            report.append(
                f"**Winner**: {winner_info['winner']} ({winner_info['score']}/100, +{winner_info['delta']} delta)"
            )

        for project in project_names:
            domain_data = projects[project].get(domain_id, {})
            scoring = domain_data.get("scoring", {})
            report.append(f"\n#### {project}")
            report.append(
                f"- **Score**: {scoring.get('score', 'N/A')}/100 ({scoring.get('grade', 'N/A')})"
            )
            for detail in scoring.get("details", []):
                report.append(f"  - {detail}")
        report.append("")

    # Winner Summary
    report.append("## Winner Summary\n")
    report.append("| Domain | Winner | Score | Delta |")
    report.append("|--------|--------|-------|-------|")
    for domain_id, domain_name in DOMAIN_NAMES.items():
        w = winners.get(domain_id, {})
        report.append(
            f"| {domain_name} | {w.get('winner', '—')} | {w.get('score', '—')} | +{w.get('delta', 0)} |"
        )

    # Recommendations
    report.append("\n## Recommendations\n")
    report.append(
        "Based on the analysis, the following integration opportunities exist:\n"
    )

    # Find weak areas per project
    for project in project_names:
        weak = []
        for domain_id, domain_name in DOMAIN_NAMES.items():
            score = (
                projects[project]
                .get(domain_id, {})
                .get("scoring", {})
                .get("score", 100)
            )
            if score < 70:
                weak.append(f"{domain_name} ({score}/100)")
        if weak:
            report.append(f"### {project} — Areas for Improvement")
            for w in weak:
                report.append(f"- {w}")
            report.append("")

    report_text = "\n".join(report)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report_text)
        print(
            json.dumps(
                {
                    "status": "success",
                    "output": str(out),
                    "projects": len(project_names),
                }
            )
        )
    else:
        print(report_text)

    return report_text


def main():
    output_path = None
    result_paths = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--results-dir" and i + 1 < len(sys.argv):
            result_paths.append(sys.argv[i + 1])
            i += 2
        else:
            result_paths.append(sys.argv[i])
            i += 1

    if not result_paths:
        print(
            json.dumps(
                {
                    "error": "Usage: generate_comparison_report.py [--output path] <result.json> ..."
                }
            )
        )
        sys.exit(1)

    projects = load_results(result_paths)
    if not projects:
        print(json.dumps({"error": "No valid results loaded"}))
        sys.exit(1)

    generate_report(projects, output_path)


if __name__ == "__main__":
    main()
