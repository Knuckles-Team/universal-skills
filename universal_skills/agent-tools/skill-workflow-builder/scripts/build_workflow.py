#!/usr/bin/env python3
"""Scaffold and validate pure atomic-skill workflows."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - the skill extra installs PyYAML
    yaml = None

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MCP_TOOL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TRIGGER_RE = re.compile(r"\buse when\b", re.IGNORECASE)
STEP_RE = re.compile(
    r"^###\s+Step\s+(\d+):\s*([a-z0-9]+(?:-[a-z0-9]+)*)"
    r"(?:\s*\[depends_on:\s*([^\]]+)\])?\s*$",
    re.MULTILINE | re.IGNORECASE,
)
DESCRIPTION_MAX = 1024
INLINE_KEYS = ("description", "expected", "instructions", "prompt", "command")
DELEGATION_FOOTER = (
    "**Execution:** If graph-os is reachable, offload the whole DAG via "
    "`graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) "
    "for true parallel/swarm execution. Otherwise execute the steps natively in "
    "dependency order: run steps with no unmet `depends_on` in parallel, then "
    "their dependents."
)


def slug(value: str) -> str:
    """Normalize a label to a portable workflow node identifier."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def validate_identifier(value: str, label: str) -> list[str]:
    errors: list[str] = []
    if not NAME_RE.fullmatch(value):
        errors.append(f"{label} must use lowercase kebab-case")
    if len(value) > 64:
        errors.append(f"{label} must be at most 64 characters")
    return errors


def validate_description(description: str) -> list[str]:
    errors: list[str] = []
    if not description.strip():
        errors.append("description must not be empty")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"description must be at most {DESCRIPTION_MAX} characters")
    if "<" in description or ">" in description:
        errors.append("description must not contain angle brackets")
    if not TRIGGER_RE.search(description):
        errors.append("description must include an explicit 'Use when' trigger")
    return errors


def get_default_workflows_root() -> Path:
    """Return this checkout's ``universal_skills`` catalog root."""
    for parent in Path(__file__).resolve().parents:
        if parent.name == "universal_skills":
            return parent
    return Path.cwd() / "universal_skills"


def _find_catalog_root(path: Path) -> Path | None:
    for candidate in (path.resolve(), *path.resolve().parents):
        if candidate.name == "universal_skills":
            return candidate
    return None


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str, str | None]:
    if not content.startswith("---"):
        return {}, content, "SKILL.md is missing YAML frontmatter"
    parts = content.split("---", 2)
    if len(parts) != 3:
        return {}, content, "SKILL.md has unterminated YAML frontmatter"
    if yaml is None:
        return {}, parts[2], "PyYAML is required to parse workflows"
    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        return {}, parts[2], f"invalid YAML frontmatter: {type(exc).__name__}"
    if not isinstance(frontmatter, dict):
        return {}, parts[2], "YAML frontmatter must be a mapping"
    return frontmatter, parts[2], None


def discover_atomic_skills(catalog_root: Path) -> set[str]:
    """Return explicitly atomic skill names discoverable in a catalog."""
    names: set[str] = set()
    if not catalog_root.is_dir():
        return names
    for skill_md in sorted(catalog_root.rglob("SKILL.md")):
        relative = skill_md.relative_to(catalog_root)
        if "assets" in relative.parts or "skill_graphs" in relative.parts:
            continue
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        frontmatter, _, error = _parse_frontmatter(content)
        if error is None and frontmatter.get("skill_type") == "skill":
            name = str(frontmatter.get("name", skill_md.parent.name))
            if NAME_RE.fullmatch(name):
                names.add(name)
    return names


def _normalize_steps(
    raw_steps: Sequence[dict[str, Any]],
) -> tuple[list[dict], list[str]]:
    steps: list[dict] = []
    errors: list[str] = []
    if not raw_steps:
        return [], ["workflow must contain at least one step"]

    for position, raw in enumerate(raw_steps, start=1):
        if not isinstance(raw, dict):
            errors.append(f"step entry {position} must be an object")
            continue
        number = raw.get("step")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            errors.append(f"step entry {position} must have a positive integer 'step'")
            continue

        skill_value = raw.get("skill")
        mcp_tool_value = raw.get("mcp_tool")
        skill = str(skill_value).strip() if skill_value else ""
        mcp_tool = str(mcp_tool_value).strip() if mcp_tool_value else ""
        package = str(raw.get("package") or "").strip()
        if bool(skill) == bool(mcp_tool):
            errors.append(
                f"Step {number} must define exactly one of 'skill' or 'mcp_tool'"
            )
        if skill:
            errors.extend(validate_identifier(skill, f"Step {number} skill"))
        if mcp_tool and not MCP_TOOL_RE.fullmatch(mcp_tool):
            errors.append(
                f"Step {number} mcp_tool must name exactly one tool without spaces or commas"
            )
        if package and not skill:
            errors.append(f"Step {number} package is valid only with a skill binding")
        if package and not PACKAGE_RE.fullmatch(package):
            errors.append(f"Step {number} package is not a valid distribution name")

        component = str(
            raw.get("id") or raw.get("component") or skill or slug(mcp_tool)
        ).strip()
        errors.extend(validate_identifier(component, f"Step {number} id"))
        agent = str(raw.get("agent") or "workflow-executor").strip()
        errors.extend(validate_identifier(agent, f"Step {number} agent"))

        dependencies = raw.get("depends_on", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list) or not all(
            isinstance(item, (str, int)) for item in dependencies
        ):
            errors.append(f"Step {number} depends_on must be a list of step references")
            dependencies = []
        inline = [key for key in INLINE_KEYS if raw.get(key)]
        if inline:
            errors.append(
                f"Step {number} contains inline workflow logic: {', '.join(inline)}"
            )

        steps.append(
            {
                "step": number,
                "component": component,
                "skill": skill or None,
                "package": package or None,
                "mcp_tool": mcp_tool or None,
                "agent": agent,
                "depends_on": [str(item).strip() for item in dependencies],
                "inline_lines": list(raw.get("inline_lines", [])),
            }
        )
    return steps, errors


def _analyze_dag(steps: Sequence[dict]) -> tuple[dict[str, list[str]], list[str]]:
    """Resolve dependencies to node identifiers and detect malformed DAGs."""
    errors: list[str] = []
    numbers = [step["step"] for step in steps]
    components = [step["component"] for step in steps]
    if len(numbers) != len(set(numbers)):
        errors.append("duplicate step numbers found")
    if len(components) != len(set(components)):
        errors.append("duplicate workflow node identifiers found")

    number_to_component = {step["step"]: step["component"] for step in steps}
    component_to_number = {step["component"]: step["step"] for step in steps}
    dependencies: dict[str, list[str]] = {step["component"]: [] for step in steps}

    for step in steps:
        for reference in step["depends_on"]:
            if reference.lower() in {"", "none", "[]"}:
                continue
            numeric = re.fullmatch(r"(?:step[ -]?)?(\d+)", reference, re.IGNORECASE)
            if numeric:
                dependency_number = int(numeric.group(1))
                dependency = number_to_component.get(dependency_number)
            else:
                dependency = slug(reference)
                dependency_number = component_to_number.get(dependency)
                if dependency_number is None:
                    dependency = None
            if dependency is None:
                errors.append(
                    f"Step {step['step']} depends on unknown step '{reference}'"
                )
                continue
            if dependency_number is not None and dependency_number >= step["step"]:
                errors.append(
                    f"Step {step['step']} dependency '{reference}' must reference an earlier step"
                )
            if dependency not in dependencies[step["component"]]:
                dependencies[step["component"]].append(dependency)

    state = {component: 0 for component in components}

    def visit(component: str) -> bool:
        state[component] = 1
        for dependency in dependencies.get(component, []):
            if dependency not in state:
                continue
            if state[dependency] == 1 or (state[dependency] == 0 and visit(dependency)):
                return True
        state[component] = 2
        return False

    if any(state[node] == 0 and visit(node) for node in state):
        errors.append("circular dependency detected in workflow steps")
    return dependencies, errors


def validate_steps_dag(steps: Sequence[dict]) -> tuple[bool, list[str]]:
    """Validate step identity, dependency references, ordering, and cycles."""
    normalized, errors = _normalize_steps(steps)
    _, dag_errors = _analyze_dag(normalized)
    errors.extend(dag_errors)
    return not errors, errors


def validate_step_bindings(
    steps: Sequence[dict], catalog_root: Path, requires: Sequence[str] = ()
) -> list[str]:
    """Require every node to bind to one atomic skill or one explicit MCP tool."""
    atomic_skills = discover_atomic_skills(catalog_root)
    required_packages = set(requires)
    errors: list[str] = []
    for step in steps:
        if step.get("skill") and step["skill"] not in atomic_skills:
            package = step.get("package")
            if not package:
                errors.append(
                    f"Step {step['step']} references missing or non-atomic skill "
                    f"'{step['skill']}' without a package owner"
                )
            elif package not in required_packages:
                errors.append(
                    f"Step {step['step']} package '{package}' must be declared in requires"
                )
        elif step.get("skill") and step.get("package"):
            errors.append(
                f"Step {step['step']} binds local skill '{step['skill']}' but also declares a package owner"
            )
        if step.get("mcp_tool") and not MCP_TOOL_RE.fullmatch(step["mcp_tool"]):
            errors.append(f"Step {step['step']} does not name one explicit MCP tool")
    return errors


def _prepare_steps(
    raw_steps: Sequence[dict[str, Any]],
    catalog_root: Path,
    requires: Sequence[str] = (),
) -> tuple[list[dict], list[str]]:
    steps, errors = _normalize_steps(raw_steps)
    dependencies, dag_errors = _analyze_dag(steps)
    errors.extend(dag_errors)
    errors.extend(validate_step_bindings(steps, catalog_root, requires))
    for step in steps:
        step["depends_on"] = dependencies.get(step["component"], [])
        if step.get("inline_lines"):
            errors.append(
                f"Step {step['step']} contains inline prose; workflows may only bind capabilities"
            )
    return sorted(steps, key=lambda item: item["step"]), errors


def _execution_levels(steps: Sequence[dict]) -> list[list[dict]]:
    remaining = {step["component"]: step for step in steps}
    completed: set[str] = set()
    levels: list[list[dict]] = []
    while remaining:
        ready = sorted(
            (
                step
                for step in remaining.values()
                if set(step["depends_on"]).issubset(completed)
            ),
            key=lambda item: item["step"],
        )
        if not ready:
            raise ValueError("workflow DAG cannot be topologically sorted")
        levels.append(ready)
        for step in ready:
            completed.add(step["component"])
            del remaining[step["component"]]
    return levels


def _build_team_config(
    workflow_name: str, description: str, steps: Sequence[dict]
) -> dict[str, Any]:
    specialists: list[str] = []
    assignments: dict[str, list[str]] = {}
    for step in steps:
        agent = step["agent"]
        capability = step.get("skill") or step.get("mcp_tool")
        if agent not in specialists:
            specialists.append(agent)
        assignments.setdefault(agent, [])
        if capability not in assignments[agent]:
            assignments[agent].append(capability)
    execution_mode = (
        "parallel"
        if any(len(level) > 1 for level in _execution_levels(steps))
        else "sequential"
    )
    return {
        "name": f"{workflow_name.replace('-', '_')}_team",
        "task_pattern": description,
        "execution_mode": execution_mode,
        "specialist_ids": specialists,
        "tool_assignments": assignments,
    }


def _render_execution(steps: Sequence[dict]) -> str:
    levels = _execution_levels(steps)
    lines = [
        "## Execution",
        "",
        "Run this workflow as a dependency-ordered DAG. Steps with no unmet "
        "`depends_on` run in parallel; dependents run after their prerequisites "
        "complete.",
        "",
    ]
    for index, level in enumerate(levels):
        rendered = "; ".join(
            f"Step {step['step']} — {step['component']}" for step in level
        )
        label = "Run first (in parallel)" if index == 0 else f"After level {index - 1}"
        lines.append(f"- **{label}:** {rendered}")
    lines.extend(["", DELEGATION_FOOTER])
    return "\n".join(lines)


def _render_workflow_body(
    workflow_name: str, description: str, steps: Sequence[dict]
) -> str:
    title = " ".join(word.capitalize() for word in workflow_name.split("-"))
    lines = [f"# {title} Workflow", "", description, "", "## Steps", ""]
    for step in steps:
        dependencies = ", ".join(step["depends_on"]) or "none"
        lines.append(
            f"### Step {step['step']}: {step['component']} [depends_on: {dependencies}]"
        )
        lines.append(f"**Agent**: `{step['agent']}`")
        if step.get("skill"):
            lines.append(f"**Skill**: `{step['skill']}`")
            if step.get("package"):
                lines.append(f"**Package**: `{step['package']}`")
        else:
            lines.append(f"**MCP Tool**: `{step['mcp_tool']}`")
        lines.append("")
    lines.append(_render_execution(steps))
    return "\n".join(lines) + "\n"


def parse_workflow_skill(skill_md_path: Path) -> dict[str, Any] | None:
    """Parse workflow metadata, pure bindings, and dependency annotations."""
    if not skill_md_path.is_file():
        return None
    content = skill_md_path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body, error = _parse_frontmatter(content)
    if error:
        return {"path": skill_md_path, "error": error, "steps": []}

    matches = list(STEP_RE.finditer(body))
    steps: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : end]
        next_section = re.search(r"^##\s+", block, re.MULTILINE)
        if next_section:
            block = block[: next_section.start()]
        dependencies = []
        if match.group(3) and match.group(3).strip().lower() not in {"none", "[]"}:
            dependencies = [
                item.strip() for item in match.group(3).split(",") if item.strip()
            ]

        def field(label: str) -> str | None:
            value = re.search(
                rf"^\*\*{re.escape(label)}\*\*:\s*`([^`]+)`\s*$",
                block,
                re.MULTILINE,
            )
            return value.group(1).strip() if value else None

        recognized = re.compile(
            r"^\*\*(?:Agent|Skill|Package|MCP Tool)\*\*:\s*`[^`]+`\s*$"
        )
        inline_lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip() and not recognized.fullmatch(line.strip())
        ]
        steps.append(
            {
                "step": int(match.group(1)),
                "component": match.group(2).lower(),
                "skill": field("Skill"),
                "package": field("Package"),
                "mcp_tool": field("MCP Tool"),
                "agent": field("Agent") or "",
                "depends_on": dependencies,
                "dependency_declared": match.group(3) is not None,
                "inline_lines": inline_lines,
            }
        )

    return {
        "path": skill_md_path,
        "frontmatter": frontmatter,
        "body": body,
        "name": frontmatter.get("name", skill_md_path.parent.name),
        "skill_type": frontmatter.get("skill_type", ""),
        "description": frontmatter.get("description", ""),
        "domain": frontmatter.get("domain", ""),
        "tags": frontmatter.get("tags", []),
        "requires": frontmatter.get("requires", []),
        "steps": steps,
    }


def validate_workflow_files(
    skill_md_path: Path, catalog_root: Path | None = None
) -> list[str]:
    """Validate metadata, bindings, DAG, team parity, and execution parity."""
    parsed = parse_workflow_skill(skill_md_path)
    if parsed is None:
        return ["configured workflow file was not found"]
    if parsed.get("error"):
        return [parsed["error"]]

    root = catalog_root or _find_catalog_root(skill_md_path)
    if root is None or not root.is_dir():
        return ["could not locate the universal_skills catalog root"]
    errors: list[str] = []
    name = str(parsed["name"])
    domain = str(parsed["domain"])
    errors.extend(validate_identifier(name, "workflow name"))
    errors.extend(validate_identifier(domain, "workflow domain"))
    if name != skill_md_path.parent.name:
        errors.append("frontmatter name must equal the workflow directory name")
    if domain != skill_md_path.parent.parent.name:
        errors.append("frontmatter domain must equal the containing domain")
    if not domain.endswith("-workflows"):
        errors.append("workflow domain must end with '-workflows'")
    if parsed["skill_type"] != "workflow":
        errors.append("skill_type must be 'workflow'")
    errors.extend(validate_description(str(parsed["description"])))

    frontmatter = parsed["frontmatter"]
    orchestrator = str(frontmatter.get("agent", ""))
    errors.extend(validate_identifier(orchestrator, "workflow agent"))
    if any(not step.get("dependency_declared") for step in parsed["steps"]):
        errors.append("every workflow step must declare depends_on, including roots")

    requires = frontmatter.get("requires") or []
    if not isinstance(requires, list) or not all(
        isinstance(item, str) and PACKAGE_RE.fullmatch(item) for item in requires
    ):
        errors.append("requires must be a list of valid package distribution names")
        requires = []
    steps, step_errors = _prepare_steps(parsed["steps"], root, requires)
    errors.extend(step_errors)
    if step_errors:
        return errors

    expected_team = _build_team_config(name, str(parsed["description"]), steps)
    if frontmatter.get("team_config") != expected_team:
        errors.append("frontmatter team_config does not match workflow bindings")

    team_path = skill_md_path.parent / "references" / "team.yaml"
    if not team_path.is_file():
        errors.append("missing references/team.yaml")
    elif yaml is not None:
        try:
            team = yaml.safe_load(team_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            errors.append(f"invalid references/team.yaml: {type(exc).__name__}")
        else:
            if team != expected_team:
                errors.append(
                    "references/team.yaml does not match frontmatter team_config"
                )

    expected_execution = _render_execution(steps)
    if expected_execution not in parsed["body"]:
        errors.append(
            "## Execution does not match the dependency DAG or standard footer"
        )
    return errors


def index_all_workflows(root_path: Path) -> list[dict[str, Any]]:
    """Find explicitly typed workflow skills recursively."""
    workflows: list[dict[str, Any]] = []
    if not root_path.is_dir():
        return workflows
    for path in sorted(root_path.rglob("SKILL.md")):
        if "assets" in path.relative_to(root_path).parts:
            continue
        parsed = parse_workflow_skill(path)
        if parsed and parsed.get("skill_type") == "workflow":
            workflows.append(parsed)
    return workflows


def scaffold_workflow_files(
    workflow_name: str,
    domain: str,
    description: str,
    tags: Sequence[str],
    requires: Sequence[str],
    steps: Sequence[dict[str, Any]],
    root_path: Path,
    orchestrator: str = "workflow-orchestrator",
) -> Path | None:
    """Write a complete dual-mode workflow after validating every binding."""
    root_path = root_path.resolve()
    errors = validate_identifier(workflow_name, "workflow name")
    errors.extend(validate_identifier(domain, "workflow domain"))
    errors.extend(validate_identifier(orchestrator, "workflow agent"))
    errors.extend(validate_description(description))
    if root_path.name != "universal_skills":
        errors.append("root_path must point to a universal_skills catalog")
    if not domain.endswith("-workflows"):
        errors.append("workflow domain must end with '-workflows'")
    invalid_requires = [
        item
        for item in requires
        if not isinstance(item, str) or not PACKAGE_RE.fullmatch(item)
    ]
    if invalid_requires:
        errors.append("requires contains invalid package distribution names")
    if not invalid_requires and len(requires) != len(set(requires)):
        errors.append("requires contains duplicate package distribution names")
    prepared_steps, step_errors = _prepare_steps(steps, root_path, requires)
    errors.extend(step_errors)
    if yaml is None:
        errors.append(
            "PyYAML is required; install universal-skills[skill-workflow-builder]"
        )
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return None

    destination = root_path / domain / workflow_name
    if destination.exists():
        print(
            f"Error: workflow directory already exists: {destination}", file=sys.stderr
        )
        return None

    team_config = _build_team_config(workflow_name, description, prepared_steps)
    frontmatter = {
        "name": workflow_name,
        "domain": domain,
        "skill_type": "workflow",
        "description": description,
        "agent": orchestrator,
        "team_config": team_config,
        "license": "MIT",
        "tags": list(tags) or ["workflow"],
        "requires": list(requires),
        "metadata": {"version": "1.2.1", "author": "Genius"},
    }
    frontmatter_text = yaml.safe_dump(
        frontmatter, sort_keys=False, allow_unicode=True
    ).strip()
    skill_text = f"---\n{frontmatter_text}\n---\n\n" + _render_workflow_body(
        workflow_name, description, prepared_steps
    )

    try:
        references = destination / "references"
        references.mkdir(parents=True, exist_ok=False)
        (destination / "SKILL.md").write_text(skill_text, encoding="utf-8")
        (references / "team.yaml").write_text(
            yaml.safe_dump(team_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    except OSError as exc:
        shutil.rmtree(destination, ignore_errors=True)
        print(f"Error: failed to scaffold workflow: {type(exc).__name__}", file=sys.stderr)
        return None

    print(f"Created workflow: {destination}")
    return destination


def _interactive_steps() -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    number = 1
    while True:
        binding_kind = (
            input(f"Step {number} binding [skill/mcp, Enter to finish]: ")
            .strip()
            .lower()
        )
        if not binding_kind:
            if steps:
                return steps
            print("At least one step is required.", file=sys.stderr)
            continue
        if binding_kind not in {"skill", "mcp"}:
            print("Choose 'skill' or 'mcp'.", file=sys.stderr)
            continue
        binding = input(
            "Atomic skill name: " if binding_kind == "skill" else "Exact MCP tool: "
        ).strip()
        package = ""
        if binding_kind == "skill":
            package = input("Package owner for an external skill [local]: ").strip()
        node_id = input("Optional unique node id: ").strip()
        agent = input("Specialist id [workflow-executor]: ").strip()
        dependencies = input("Earlier nodes or Step N, comma-separated: ").strip()
        step: dict[str, Any] = {
            "step": number,
            "agent": agent or "workflow-executor",
            "depends_on": [
                item.strip() for item in dependencies.split(",") if item.strip()
            ],
        }
        step["skill" if binding_kind == "skill" else "mcp_tool"] = binding
        if package:
            step["package"] = package
        if node_id:
            step["id"] = node_id
        steps.append(step)
        number += 1


def _handle_scaffold(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else get_default_workflows_root()
    if args.interactive:
        steps = _interactive_steps()
    elif args.steps_json:
        try:
            steps = json.loads(args.steps_json)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid steps JSON: {type(exc).__name__}", file=sys.stderr)
            return 1
        if not isinstance(steps, list):
            print("Error: --steps-json must contain a JSON list", file=sys.stderr)
            return 1
    else:
        print("Error: provide --steps-json or --interactive", file=sys.stderr)
        return 1
    tags = [item.strip() for item in args.tags.split(",") if item.strip()]
    requires = [item.strip() for item in args.requires.split(",") if item.strip()]
    result = scaffold_workflow_files(
        args.name,
        args.domain,
        args.description,
        tags,
        requires,
        steps,
        root,
        orchestrator=args.orchestrator,
    )
    return 0 if result else 1


def _handle_validate(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    root = Path(args.root).resolve() if args.root else _find_catalog_root(path)
    errors = validate_workflow_files(path, root)
    if errors:
        print("Workflow validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Workflow is valid: {path}")
    return 0


def _handle_list(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else get_default_workflows_root()
    workflows = index_all_workflows(root)
    for workflow in workflows:
        print(
            f"{workflow['domain']}/{workflow['name']} ({len(workflow['steps'])} steps)"
        )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List workflow metadata")
    list_parser.add_argument("--root", help="Path to the universal_skills catalog")
    list_parser.set_defaults(handler=_handle_list)

    scaffold_parser = subparsers.add_parser(
        "scaffold", help="Scaffold a pure skill workflow"
    )
    scaffold_parser.add_argument("name", help="Lowercase kebab-case workflow name")
    scaffold_parser.add_argument(
        "--domain", required=True, help="A top-level *-workflows domain"
    )
    scaffold_parser.add_argument(
        "--description",
        required=True,
        help="Routing description containing what it does and 'Use when'",
    )
    scaffold_parser.add_argument("--tags", default="workflow")
    scaffold_parser.add_argument("--requires", default="")
    scaffold_parser.add_argument("--root", help="Path to the universal_skills catalog")
    scaffold_parser.add_argument("--orchestrator", default="workflow-orchestrator")
    step_mode = scaffold_parser.add_mutually_exclusive_group(required=True)
    step_mode.add_argument("--interactive", action="store_true")
    step_mode.add_argument("--steps-json", help="JSON list of pure workflow nodes")
    scaffold_parser.set_defaults(handler=_handle_scaffold)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate a complete workflow"
    )
    validate_parser.add_argument("path", help="Path to the workflow SKILL.md")
    validate_parser.add_argument("--root", help="Path to the universal_skills catalog")
    validate_parser.set_defaults(handler=_handle_validate)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
