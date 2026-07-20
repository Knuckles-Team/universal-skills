#!/usr/bin/env python3
"""Audit canonical SKILL.md entries and emit actionable structural findings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # pragma: no cover - surfaced as a clear CLI error
    yaml = None

DESCRIPTION_MAX = 1024
SKILL_TYPES = {"skill", "workflow", "graph"}
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MCP_TOOL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
STEP_RE = re.compile(
    r"^###\s+Step\s+(\d+):\s*([^\n\[]+?)((?:\s*\[[^\]]+\])*)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
TRIGGER_RE = re.compile(
    r"\b(use when|use for|trigger(?:s|ed)? (?:on|when)|when (?:the )?(?:user|agent))\b",
    re.IGNORECASE,
)
GENERIC_DESCRIPTION_RE = re.compile(
    r"^parallel execution workflow for .+ using the unified parallel engine\.?$",
    re.IGNORECASE,
)
PLACEHOLDER_STEP_RE = re.compile(
    r"^execute .+ operations for the .+ workflow\.?$", re.IGNORECASE
)
DELEGATION_MARKER = "graph_orchestrate"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class Step:
    number: int
    component: str
    depends_on: list[str]
    body: str
    tools: list[str] = field(default_factory=list)
    skill_ref: str = ""
    mcp_tool: str = ""
    package: str = ""

    @property
    def node_id(self) -> str:
        return slug(self.component)


@dataclass
class SkillAudit:
    path: str
    name: str
    domain: str
    skill_type: str
    description: str
    body_lines: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def status(self) -> str:
        severities = {finding.severity for finding in self.findings}
        if "error" in severities:
            return "error"
        if "warning" in severities:
            return "warning"
        return "clean"


@dataclass
class CatalogAudit:
    root: str
    skills: list[SkillAudit]

    @property
    def finding_counts(self) -> Counter:
        return Counter(
            finding.severity
            for skill in self.skills
            for finding in skill.findings
        )

    @property
    def code_counts(self) -> Counter:
        return Counter(
            finding.code for skill in self.skills for finding in skill.findings
        )


def slug(value: str) -> str:
    """Normalize a workflow label to the compiler's node-id dialect."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str | None]:
    if yaml is None:
        return {}, "PyYAML is required; install universal-skills[skill-catalog-auditor]"
    fm_text, _ = split_frontmatter(text)
    if not fm_text.strip():
        return {}, "missing YAML frontmatter"
    try:
        parsed = yaml.safe_load(fm_text)
    except Exception as exc:  # noqa: BLE001
        return {}, f"invalid YAML frontmatter: {type(exc).__name__}"
    if not isinstance(parsed, dict):
        return {}, "frontmatter must be a mapping"
    return parsed, None


def parse_steps(body: str) -> list[Step]:
    matches = list(STEP_RE.finditer(body))
    steps: list[Step] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : end]
        next_section = re.search(r"^##\s+", block, re.MULTILINE)
        if next_section:
            block = block[: next_section.start()]
        annotations = {
            key.lower(): value.strip()
            for key, value in re.findall(
                r"\[([a-z_]+):\s*([^\]]*)\]", match.group(3) or "", re.IGNORECASE
            )
        }
        dependency_text = annotations.get("depends_on", "")
        dependencies = []
        if dependency_text.lower() not in {"", "none", "[]"}:
            dependencies = [
                item.strip() for item in dependency_text.split(",") if item.strip()
            ]
        tools_match = re.search(r"^\*\*Tools\*\*:\s*`?([^`\n]+)`?", block, re.MULTILINE)
        tools = []
        if tools_match:
            tools = [item.strip() for item in tools_match.group(1).split(",") if item.strip()]
        skill_match = re.search(
            r"^\*\*Skill\*\*:\s*`([^`]+)`\s*$", block, re.MULTILINE
        )
        package_match = re.search(
            r"^\*\*Package\*\*:\s*`([^`]+)`\s*$", block, re.MULTILINE
        )
        mcp_match = re.search(
            r"^\*\*MCP Tool\*\*:\s*`([^`]+)`\s*$", block, re.MULTILINE
        )
        steps.append(
            Step(
                number=int(match.group(1)),
                component=match.group(2).strip(),
                depends_on=dependencies,
                body=block.strip(),
                tools=tools,
                skill_ref=annotations.get("skill", "")
                or (skill_match.group(1).strip() if skill_match else ""),
                mcp_tool=annotations.get("mcp_tool", "")
                or (mcp_match.group(1).strip() if mcp_match else ""),
                package=package_match.group(1).strip() if package_match else "",
            )
        )
    return steps


def meaningful_step_prose(step: Step) -> str:
    lines = []
    for raw_line in step.body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(
            (
                "**Agent**:",
                "**Tools**:",
                "**Skill**:",
                "**Package**:",
                "**MCP Tool**:",
                "Expected:",
            )
        ):
            continue
        lines.append(line)
    return " ".join(lines)


def is_kg_placeholder(prose: str) -> bool:
    return prose.startswith(
        "Persist workflow results as nodes and edges in the Knowledge Graph."
    ) and "Create appropriate typed nodes with metadata" in prose


def resolve_dependency(
    dependency: str,
    number_to_node: dict[int, str],
    known_nodes: set[str],
) -> str | None:
    cleaned = dependency.strip()
    numeric = re.fullmatch(r"(?:step[ -]?)?(\d+)", cleaned, re.IGNORECASE)
    if numeric:
        return number_to_node.get(int(numeric.group(1)))
    candidate = slug(cleaned)
    return candidate if candidate in known_nodes else None


def cycle_nodes(graph: dict[str, set[str]]) -> set[str]:
    state = {node: 0 for node in graph}
    cycle: set[str] = set()

    def visit(node: str) -> None:
        state[node] = 1
        for dependency in graph[node]:
            if dependency not in graph:
                continue
            if state[dependency] == 1:
                cycle.update((node, dependency))
            elif state[dependency] == 0:
                visit(dependency)
        state[node] = 2

    for node in graph:
        if state[node] == 0:
            visit(node)
    return cycle


def local_link_findings(skill_md: Path, root: Path, body: str) -> list[Finding]:
    findings = []
    prose = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    for raw_target in LINK_RE.findall(prose):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        if any(token in target for token in ("{", "}", "*", "[", "]")):
            continue
        target_path = (skill_md.parent / unquote(target)).resolve()
        if not target_path.exists():
            rel = skill_md.relative_to(root).as_posix()
            findings.append(
                Finding("error", "broken-local-link", f"{rel} links to missing `{target}`")
            )
    return findings


def workflow_findings(
    skill_md: Path,
    root: Path,
    fm: dict[str, Any],
    body: str,
    atomic_names: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    steps = parse_steps(body)
    if not steps:
        return [Finding("error", "workflow-no-steps", "workflow has no `### Step N:` DAG")]

    numbers = [step.number for step in steps]
    nodes = [step.node_id for step in steps]
    if len(numbers) != len(set(numbers)):
        findings.append(Finding("error", "workflow-duplicate-number", "step numbers are not unique"))
    if len(nodes) != len(set(nodes)):
        findings.append(Finding("error", "workflow-duplicate-component", "step component names are not unique"))

    number_to_node = {step.number: step.node_id for step in steps}
    known_nodes = set(nodes)
    graph: dict[str, set[str]] = {node: set() for node in known_nodes}
    broken: list[str] = []
    for step in steps:
        for dependency in step.depends_on:
            resolved = resolve_dependency(dependency, number_to_node, known_nodes)
            if resolved is None:
                broken.append(f"{step.node_id} -> {dependency}")
            else:
                graph[step.node_id].add(resolved)
    if broken:
        findings.append(
            Finding(
                "error",
                "workflow-broken-dependency",
                "unresolvable dependencies: " + ", ".join(broken[:5]),
            )
        )
    cyclic = cycle_nodes(graph)
    if cyclic:
        findings.append(
            Finding("error", "workflow-cycle", "cycle includes: " + ", ".join(sorted(cyclic)))
        )

    placeholder_steps = []
    substantive_steps = []
    for step in steps:
        prose = meaningful_step_prose(step)
        if PLACEHOLDER_STEP_RE.fullmatch(prose) or is_kg_placeholder(prose):
            placeholder_steps.append(step.node_id)
        else:
            substantive_steps.append(step.node_id)
    if placeholder_steps and not substantive_steps:
        findings.append(
            Finding(
                "error",
                "workflow-placeholder-only",
                f"all {len(placeholder_steps)} steps contain generated placeholder prose",
            )
        )
    elif placeholder_steps:
        findings.append(
            Finding(
                "warning",
                "workflow-placeholder-step",
                "placeholder steps: " + ", ".join(placeholder_steps[:6]),
            )
        )

    team_path = skill_md.parent / "references" / "team.yaml"
    if not team_path.is_file():
        findings.append(
            Finding("error", "workflow-team-missing", "missing `references/team.yaml`")
        )
    elif yaml is not None:
        try:
            team = yaml.safe_load(team_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:  # noqa: BLE001
            findings.append(Finding("error", "workflow-team-invalid", type(exc).__name__))
            team = {}
        front_team = fm.get("team_config") or {}
        front_ids = set(front_team.get("specialist_ids") or []) if isinstance(front_team, dict) else set()
        file_ids = set(team.get("specialist_ids") or []) if isinstance(team, dict) else set()
        if front_ids and file_ids and front_ids != file_ids:
            findings.append(
                Finding(
                    "warning",
                    "workflow-team-drift",
                    "frontmatter and team.yaml specialist sets differ",
                )
            )

    if "## Execution" not in body or DELEGATION_MARKER not in body:
        findings.append(
            Finding(
                "error",
                "workflow-execution-missing",
                "missing `## Execution` or graph-os delegation footer",
            )
        )

    requires = {slug(str(item)) for item in (fm.get("requires") or [])}
    unbound = []
    for step in steps:
        component = step.node_id
        skill_binding = slug(step.skill_ref) if step.skill_ref else ""
        package_binding = slug(step.package) if step.package else ""
        valid_explicit_mcp = bool(step.mcp_tool) and bool(
            MCP_TOOL_RE.fullmatch(step.mcp_tool)
        )
        if step.mcp_tool and not valid_explicit_mcp:
            findings.append(
                Finding(
                    "error",
                    "workflow-mcp-binding-invalid",
                    f"step `{step.component}` does not name one exact MCP tool",
                )
            )
        exact_tool_binding = (
            len(step.tools) == 1 and slug(step.tools[0]) == component
        )
        explicitly_external = (
            component in requires
            or skill_binding in atomic_names
            or skill_binding in requires
            or bool(skill_binding and package_binding in requires)
            or valid_explicit_mcp
        )
        if len(step.tools) > 1:
            findings.append(
                Finding(
                    "warning",
                    "workflow-multiple-tools",
                    f"step `{step.component}` lists {len(step.tools)} tools; bind one atomic skill or one exact MCP tool",
                )
            )
        if component not in atomic_names and not explicitly_external and not exact_tool_binding:
            unbound.append(step.component)
    if unbound:
        findings.append(
            Finding(
                "warning",
                "workflow-unbound-component",
                f"{len(unbound)}/{len(steps)} steps do not name an atomic skill, declared requirement, or single MCP tool: "
                + ", ".join(unbound[:5]),
            )
        )

    team_config = fm.get("team_config") or {}
    execution_mode = str(
        team_config.get("execution_mode", "")
        if isinstance(team_config, dict)
        else team_config
    )
    if "parallel" in str(fm.get("description", "")).lower() and execution_mode == "sequential":
        findings.append(
            Finding(
                "warning",
                "workflow-mode-drift",
                "description says parallel but team_config execution_mode is sequential",
            )
        )
    return findings


def atomic_findings(fm_text: str, body: str, atomic_names: set[str], own_name: str) -> list[Finding]:
    findings: list[Finding] = []
    forbidden = [
        key for key in ("team_config", "specialist_ids", "execution_mode")
        if re.search(rf"^{key}:", fm_text, re.MULTILINE)
    ]
    if forbidden:
        findings.append(
            Finding(
                "error",
                "atomic-workflow-metadata",
                "atomic skill contains workflow metadata: " + ", ".join(forbidden),
            )
        )
    if re.search(r"^###\s+Step\s+\d+:.*\[depends_on:", body, re.MULTILINE):
        findings.append(
            Finding("warning", "atomic-dependency-dag", "atomic skill embeds a dependency DAG")
        )
    referenced = sorted(
        name
        for name in atomic_names - {own_name}
        if re.search(rf"(?:\$|`){re.escape(name)}(?:`|\b)", body)
    )
    if len(referenced) >= 2:
        findings.append(
            Finding(
                "warning",
                "atomic-cross-skill-orchestration",
                "references multiple atomic skills; verify this is not a workflow: "
                + ", ".join(referenced[:5]),
            )
        )
    if re.search(r"^##\s+Workflows?\b", body, re.MULTILINE | re.IGNORECASE):
        findings.append(
            Finding(
                "warning",
                "atomic-workflow-section",
                "contains a Workflow section; confirm it describes one capability only",
            )
        )
    return findings


def audit_catalog(root: Path) -> CatalogAudit:
    root = root.resolve()
    parsed: list[tuple[Path, str, str, dict[str, Any], str | None]] = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        rel_parts = skill_md.relative_to(root).parts
        if "assets" in rel_parts or "skill_graphs" in rel_parts:
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        fm, error = parse_frontmatter(text)
        _, body = split_frontmatter(text)
        parsed.append((skill_md, text, body, fm, error))

    atomic_names = {
        slug(str(fm.get("name", path.parent.name)))
        for path, _, _, fm, error in parsed
        if error is None and fm.get("skill_type") == "skill"
    }
    audits: list[SkillAudit] = []
    seen_names: dict[str, str] = {}

    for skill_md, text, body, fm, parse_error in parsed:
        rel = skill_md.relative_to(root).as_posix()
        top_domain = skill_md.relative_to(root).parts[0]
        name = str(fm.get("name", skill_md.parent.name))
        domain = str(fm.get("domain", ""))
        skill_type = str(fm.get("skill_type", ""))
        description = str(fm.get("description", ""))
        audit = SkillAudit(rel, name, domain, skill_type, description, len(body.splitlines()))
        fm_text, _ = split_frontmatter(text)

        if parse_error:
            audit.findings.append(Finding("error", "frontmatter-invalid", parse_error))
            audits.append(audit)
            continue
        if not KEBAB_RE.fullmatch(name):
            audit.findings.append(Finding("error", "name-invalid", "name must be kebab-case"))
        if name != skill_md.parent.name:
            audit.findings.append(
                Finding("error", "name-path-mismatch", f"name `{name}` != directory `{skill_md.parent.name}`")
            )
        if name in seen_names:
            audit.findings.append(
                Finding("error", "name-duplicate", f"also declared by `{seen_names[name]}`")
            )
        else:
            seen_names[name] = rel
        if domain != top_domain:
            audit.findings.append(
                Finding("error", "domain-mismatch", f"domain `{domain}` != top-level directory `{top_domain}`")
            )
        if skill_type not in SKILL_TYPES:
            audit.findings.append(
                Finding("error", "skill-type-invalid", f"skill_type must be one of {sorted(SKILL_TYPES)}")
            )
        if not description.strip():
            audit.findings.append(Finding("error", "description-missing", "description is empty"))
        elif len(description) > DESCRIPTION_MAX:
            audit.findings.append(
                Finding("error", "description-too-long", f"description is {len(description)} characters")
            )
        else:
            if not TRIGGER_RE.search(description):
                audit.findings.append(
                    Finding("warning", "description-no-trigger", "description lacks an explicit trigger phrase")
                )
            if len(description) < 80:
                audit.findings.append(
                    Finding("warning", "description-too-short", f"description is only {len(description)} characters")
                )
            if GENERIC_DESCRIPTION_RE.fullmatch(description.strip()):
                audit.findings.append(
                    Finding("warning", "description-generic", "description names the engine instead of user triggers")
                )
        if audit.body_lines > 500:
            audit.findings.append(
                Finding("warning", "body-too-long", f"SKILL.md body is {audit.body_lines} lines; use progressive disclosure")
            )
        if "ACTION REQUIRED" in text or re.search(r"\bTODO\b", text):
            audit.findings.append(
                Finding("warning", "placeholder-marker", "contains TODO/ACTION REQUIRED placeholder text")
            )
        audit.findings.extend(local_link_findings(skill_md, root, body))

        if skill_type == "workflow":
            audit.findings.extend(workflow_findings(skill_md, root, fm, body, atomic_names))
        elif skill_type == "skill":
            audit.findings.extend(atomic_findings(fm_text, body, atomic_names, slug(name)))
        audits.append(audit)

    return CatalogAudit(str(root), audits)


def summary_data(audit: CatalogAudit) -> dict[str, Any]:
    types = Counter(skill.skill_type for skill in audit.skills)
    statuses = Counter(skill.status for skill in audit.skills)
    return {
        "root": audit.root,
        "skill_count": len(audit.skills),
        "types": dict(sorted(types.items())),
        "statuses": dict(sorted(statuses.items())),
        "findings": dict(sorted(audit.finding_counts.items())),
        "codes": dict(audit.code_counts.most_common()),
    }


def render_text(audit: CatalogAudit) -> str:
    summary = summary_data(audit)
    lines = [
        f"Skill catalog: {summary['skill_count']} entries",
        f"Types: {summary['types']}",
        f"Statuses: {summary['statuses']}",
        f"Findings: {summary['findings']}",
    ]
    if summary["codes"]:
        lines.append("Finding codes: " + ", ".join(f"{key}={value}" for key, value in summary["codes"].items()))
    for skill in audit.skills:
        if not skill.findings:
            continue
        lines.append(f"\n{skill.path} [{skill.status}]")
        for finding in skill.findings:
            lines.append(f"  {finding.severity.upper():7} {finding.code}: {finding.message}")
    return "\n".join(lines) + "\n"


def render_json(audit: CatalogAudit) -> str:
    payload = summary_data(audit)
    payload["skills"] = [
        {
            **{key: value for key, value in asdict(skill).items() if key != "findings"},
            "status": skill.status,
            "findings": [asdict(finding) for finding in skill.findings],
        }
        for skill in audit.skills
    ]
    return json.dumps(payload, indent=2) + "\n"


def escape_table(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def render_markdown(audit: CatalogAudit) -> str:
    summary = summary_data(audit)
    lines = [
        "# Skill Catalog Audit",
        "",
        f"Audited **{summary['skill_count']}** skills: "
        + ", ".join(f"{value} {key}" for key, value in summary["types"].items())
        + ".",
        "",
        "This deterministic structural report excludes bundled `assets/` templates and "
        "generated `skill_graphs/`. Advisory findings require qualitative review; a clean "
        "row does not by itself prove domain correctness, safety, or freshness.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in summary["statuses"].items():
        lines.append(f"| {status} | {count} |")
    if summary["codes"]:
        lines += [
            "",
            "### Finding codes",
            "",
            "| Code | Count |",
            "|---|---:|",
        ]
        for code, count in summary["codes"].items():
            lines.append(f"| `{escape_table(code)}` | {count} |")
    lines += [
        "",
        "## Per-skill assessment",
        "",
        "| Domain | Skill | Type | Status | Findings |",
        "|---|---|---|---|---|",
    ]
    for skill in audit.skills:
        findings = "; ".join(
            f"{finding.severity}: `{finding.code}` — {finding.message}"
            for finding in skill.findings
        ) or "No structural or advisory findings"
        lines.append(
            f"| {escape_table(skill.domain)} | `{escape_table(skill.name)}` | "
            f"{escape_table(skill.skill_type)} | {skill.status} | {escape_table(findings)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="universal_skills")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        parser.error(f"catalog root does not exist: {root}")
    if yaml is None:
        print("PyYAML is required; install universal-skills[skill-catalog-auditor]", file=sys.stderr)
        return 2

    audit = audit_catalog(root)
    renderers = {"text": render_text, "json": render_json, "markdown": render_markdown}
    output = renderers[args.format](audit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")

    counts = audit.finding_counts
    if args.fail_on == "error" and counts["error"]:
        return 1
    if args.fail_on == "warning" and (counts["error"] or counts["warning"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
