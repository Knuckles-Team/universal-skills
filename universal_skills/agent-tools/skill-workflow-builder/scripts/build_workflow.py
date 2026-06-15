#!/usr/bin/env python3
"""
Skill Workflow Builder - Create, index, and topologically validate workflow-based skills.

Usage:
    python build_workflow.py list [--root <path>]
    python build_workflow.py scaffold <workflow-name> --domain <domain> --description <desc> [--root <path>]
    python build_workflow.py validate <path/to/SKILL.md>
    python build_workflow.py query-kg [--db <path>]

Examples:
    python build_workflow.py list
    python build_workflow.py scaffold check-disk-capacity --domain infra --description "Check server disk space"
"""

import sys
import os
import re
import argparse
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

try:
    import yaml
except ImportError:
    yaml = None

# ANSI colors for premium terminal UI
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_premium(text: str, color: str = ""):
    """Print premium terminal UI outputs."""
    print(f"{color}{text}{RESET}")


def get_default_workflows_root() -> Path:
    """Determine the default location of the workflows directory."""
    # Find universal_skills root
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "universal_skills":
            return parent / "workflows"
    # Fallback to local workspace assumptions
    return Path(
        "/home/apps/workspace/agent-packages/skills/universal-skills/universal_skills/workflows"
    )


def parse_workflow_skill(skill_md_path: Path) -> Optional[Dict]:
    """Parse a workflow's SKILL.md file for metadata and steps."""
    if not skill_md_path.exists():
        return None

    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        print_premium(f"❌ Error reading file {skill_md_path}: {e}", RED)
        return None

    # Parse YAML frontmatter
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            body = parts[2]
            if yaml:
                try:
                    frontmatter = yaml.safe_load(yaml_content) or {}
                except Exception as e:
                    print_premium(
                        f"⚠️ Warning: YAML parsing error in {skill_md_path}: {e}", YELLOW
                    )
            else:
                # Fallback simple line regex parsing if PyYAML is missing
                for line in yaml_content.splitlines():
                    match = re.match(r"^(\w+):\s*(.*)$", line.strip())
                    if match:
                        key, val = match.groups()
                        # Clean tags/requires lists
                        if val.startswith("[") and val.endswith("]"):
                            val = [
                                item.strip("'\" ")
                                for item in val[1:-1].split(",")
                                if item.strip()
                            ]
                        frontmatter[key] = val

    # Parse Steps
    steps = []
    # Match headings like: ### Step 0: portainer-mcp or ### Step 2: user-interaction [depends_on: Step 0]
    step_pattern = re.compile(
        r"^###\s+Step\s+(\d+):\s*([a-zA-Z0-9_-]+)(?:\s*\[depends_on:\s*([^\]]+)\])?",
        re.MULTILINE,
    )

    matches = list(step_pattern.finditer(body))
    for i, match in enumerate(matches):
        step_num = int(match.group(1))
        component = match.group(2).strip()
        depends_raw = match.group(3)

        # Calculate start and end of step description/details block
        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        step_body = body[start_idx:end_idx].strip()

        # Extract Expected and Depends On fields
        expected = None
        expected_match = re.search(r"Expected:\s*(.*)", step_body)
        if expected_match:
            expected = expected_match.group(1).strip()

        depends_on = []
        if depends_raw:
            depends_on = [d.strip() for d in depends_raw.split(",") if d.strip()]
        else:
            depends_match = re.search(r"Depends On:\s*(.*)", step_body)
            if depends_match:
                depends_on = [
                    d.strip() for d in depends_match.group(1).split(",") if d.strip()
                ]

        steps.append(
            {
                "step": step_num,
                "component": component,
                "description": step_body.split("\n")[0].strip(),
                "expected": expected,
                "depends_on": depends_on,
            }
        )

    return {
        "path": skill_md_path,
        "name": frontmatter.get("name", skill_md_path.parent.name),
        "description": frontmatter.get("description", ""),
        "domain": frontmatter.get("domain", ""),
        "tags": frontmatter.get("tags", []),
        "requires": frontmatter.get("requires", []),
        "steps": steps,
    }


def index_all_workflows(root_path: Path) -> List[Dict]:
    """Find and parse all workflow skills recursively."""
    workflows = []
    if not root_path.exists():
        print_premium(f"❌ Workflows root path does not exist: {root_path}", RED)
        return workflows

    for p in root_path.rglob("SKILL.md"):
        parsed = parse_workflow_skill(p)
        if parsed:
            workflows.append(parsed)

    return workflows


def validate_steps_dag(steps: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate that the steps form a Directed Acyclic Graph (DAG) and dependencies exist."""
    errors = []

    # Check that all step numbers are unique
    step_nums = {s["step"] for s in steps}
    if len(step_nums) != len(steps):
        errors.append("Duplicate step numbers found.")

    # Build adjacency list
    adj = {s["step"]: [] for s in steps}

    # Resolve name-based dependencies (e.g. "[depends_on: gitlab-repository-seeder]")
    # to their step number by matching the slugified component name. This makes the
    # validator accept the three dependency dialects used across the workflow corpus:
    # numeric ("Step 2" / "2"), and atomic-skill-name references.
    def _slug(s: str) -> str:
        return re.sub(r"[-\s]+", "_", s.strip().lower())

    comp_to_num = {_slug(s["component"]): s["step"] for s in steps}

    # Process dependencies
    for s in steps:
        step_num = s["step"]
        for dep in s["depends_on"]:
            # Numeric form first ("Step 0" or "0").
            dep_match = re.fullmatch(r"(?:step\s*)?(\d+)", dep.strip(), re.IGNORECASE)
            if dep_match:
                dep_num = int(dep_match.group(1))
            else:
                # Name-based form: match the slugified component name.
                dep_num = comp_to_num.get(_slug(dep))
                if dep_num is None:
                    errors.append(
                        f"Step {step_num} depends on unresolvable '{dep}' "
                        f"(not a step number or known step component)"
                    )
                    continue

            if dep_num not in step_nums:
                errors.append(f"Step {step_num} depends on non-existent Step {dep_num}")
                continue

            adj[dep_num].append(step_num)  # Edge from dep to step

    # Cycle detection using DFS
    visited = {s["step"]: 0 for s in steps}  # 0=unvisited, 1=visiting, 2=visited

    def has_cycle(u) -> bool:
        visited[u] = 1
        for v in adj[u]:
            if visited[v] == 1:
                return True
            if visited[v] == 0:
                if has_cycle(v):
                    return True
        visited[u] = 2
        return False

    for u in visited:
        if visited[u] == 0:
            if has_cycle(u):
                errors.append("Circular dependency detected in workflow steps!")
                break

    return len(errors) == 0, errors


def scaffold_workflow_files(
    workflow_name: str,
    domain: str,
    description: str,
    tags: List[str],
    requires: List[str],
    steps: List[Dict],
    root_path: Path,
) -> Optional[Path]:
    """Scaffold a new workflow's directory and default files."""
    dest_dir = root_path / domain / workflow_name
    if dest_dir.exists():
        print_premium(f"❌ Error: Workflow folder already exists: {dest_dir}", RED)
        return None

    try:
        dest_dir.mkdir(parents=True, exist_ok=False)
        print_premium(f"✅ Created folder: {dest_dir}", GREEN)
    except Exception as e:
        print_premium(f"❌ Error creating directory: {e}", RED)
        return None

    # Generate SKILL.md content
    frontmatter = {
        "name": workflow_name,
        "description": description,
        "domain": domain,
        "tags": tags,
        "requires": requires,
    }

    frontmatter_str = "---\n"
    if yaml:
        frontmatter_str += yaml.dump(frontmatter, sort_keys=False)
    else:
        # Simple fallback serializer
        frontmatter_str += f"name: {workflow_name}\n"
        frontmatter_str += f"description: {description}\n"
        frontmatter_str += f"domain: {domain}\n"
        frontmatter_str += f"tags: {json.dumps(tags)}\n"
        frontmatter_str += f"requires: {json.dumps(requires)}\n"
    frontmatter_str += "---\n\n"

    body_str = f"# {workflow_name} Workflow\n\n{description}\n\n"

    for s in steps:
        step_num = s["step"]
        component = s["component"]
        desc = s.get("description", "Perform operation")
        expected = s.get("expected", "success")
        deps = s.get("depends_on", [])

        dep_str = ""
        if deps:
            dep_str = f" [depends_on: {', '.join(deps)}]"

        body_str += f"### Step {step_num}: {component}{dep_str}\n"
        body_str += f"{desc}\n"
        body_str += f"Expected: {expected}\n\n"

    skill_md = dest_dir / "SKILL.md"
    try:
        skill_md.write_text(frontmatter_str + body_str, encoding="utf-8")
        print_premium(f"✅ Created SKILL.md in {dest_dir}", GREEN)
    except Exception as e:
        print_premium(f"❌ Error writing SKILL.md: {e}", RED)
        return None

    # Create default team.yaml reference
    references_dir = dest_dir / "references"
    try:
        references_dir.mkdir(exist_ok=True)
        team_yaml = references_dir / "team.yaml"
        team_content = f"""name: {workflow_name.replace("_", " ").title()} Swarm
task_pattern: Perform {workflow_name.replace("_", " ").title()} operations concurrently across all target layers
specialist_ids:
  - knowledge-graph
"""
        team_yaml.write_text(team_content, encoding="utf-8")
        print_premium(f"✅ Created default team.yaml in {references_dir}", GREEN)
    except Exception as e:
        print_premium(f"❌ Error creating references: {e}", RED)

    return dest_dir


def query_local_kg(db_path: Path) -> List[Tuple]:
    """Query a local SQLite Knowledge Graph database for existing workflows or specialists."""
    if not db_path.exists():
        print_premium(f"⚠️ Warning: Database file not found at {db_path}", YELLOW)
        return []

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Look for table names first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        results = []
        if "nodes" in tables:
            # Graph-OS structured schema search
            cursor.execute("SELECT node_id, node_type, properties FROM nodes LIMIT 20;")
            results = cursor.fetchall()
            print_premium(
                f"🤖 Connected to local KG database. Found {len(results)} sample nodes:",
                BLUE,
            )
            for row in results:
                print(f"  - [{row[1]}] ID: {row[0]}")
        else:
            print_premium(
                "🤖 Connected to SQLite, but did not recognize standard graph-os schema.",
                YELLOW,
            )

        conn.close()
        return results
    except Exception as e:
        print_premium(f"❌ SQLite connection failed: {e}", RED)
        return []


def handle_scaffold_flow(args):
    """Orchestrate the scaffolding command execution."""
    root_path = Path(args.root) if args.root else get_default_workflows_root()

    print_premium(
        f"🚀 Preparing to scaffold workflow: '{args.name}' under '{args.domain}' domain...",
        BOLD + BLUE,
    )

    # Gather steps interactively if steps parameter is omitted
    steps = []
    if not args.interactive and not args.steps_json:
        # Provide a default Step 0
        steps = [
            {
                "step": 0,
                "component": "user-interaction",
                "description": f"Gather user specification for {args.name}",
                "expected": "spec_details",
                "depends_on": [],
            }
        ]
    elif args.steps_json:
        try:
            steps = json.loads(args.steps_json)
        except Exception as e:
            print_premium(f"❌ Invalid steps JSON: {e}", RED)
            sys.exit(1)
    else:
        # Interactive step collection
        print_premium("\n--- Interactive Step Configuration ---", BOLD)
        step_idx = 0
        while True:
            print_premium(f"\n[Step {step_idx}]", BOLD + BLUE)
            component = input(
                "Enter component/tool (e.g. portainer-mcp, user-interaction) or press Enter to finish: "
            ).strip()
            if not component:
                if step_idx == 0:
                    print_premium("Must enter at least one step!", RED)
                    continue
                break

            description = input("Enter description of what this step does: ").strip()
            expected = input(
                "Enter expected output/variables (e.g. endpoint_id): "
            ).strip()
            deps_raw = input(
                "Enter dependencies as comma-separated step numbers (e.g. 0,1) [None]: "
            ).strip()

            depends_on = []
            if deps_raw:
                depends_on = [
                    f"Step {d.strip()}" for d in deps_raw.split(",") if d.strip()
                ]

            steps.append(
                {
                    "step": step_idx,
                    "component": component,
                    "description": description,
                    "expected": expected,
                    "depends_on": depends_on,
                }
            )
            step_idx += 1

    # Validate DAG
    is_valid, errors = validate_steps_dag(steps)
    if not is_valid:
        print_premium("❌ Step validation failed:", RED)
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    tags = (
        [t.strip() for t in args.tags.split(",") if t.strip()]
        if args.tags
        else ["workflow"]
    )
    requires = (
        [r.strip() for r in args.requires.split(",") if r.strip()]
        if args.requires
        else []
    )

    dest = scaffold_workflow_files(
        args.name, args.domain, args.description, tags, requires, steps, root_path
    )

    if dest:
        print_premium(
            f"\n🎉 Successfully created and registered workflow at {dest}!",
            BOLD + GREEN,
        )


def handle_list_flow(args):
    """Orchestrate the list command execution."""
    root_path = Path(args.root) if args.root else get_default_workflows_root()
    print_premium(f"🔍 Indexing all workflow skills in {root_path}...", BOLD + BLUE)

    workflows = index_all_workflows(root_path)
    print_premium(
        f"Found {len(workflows)} active workflow-based skills:\n", BOLD + GREEN
    )

    # Sort by domain
    by_domain = {}
    for wf in workflows:
        dom = wf["domain"] or "other"
        by_domain.setdefault(dom, []).append(wf)

    for dom, wfs in by_domain.items():
        print_premium(f"📁 Domain: {dom}", BOLD + BLUE)
        for wf in wfs:
            print(f"  - {BOLD}{wf['name']}{RESET}")
            print(f"    Description: {wf['description']}")
            print(f"    Requires: {wf['requires']}")
            print(f"    Steps ({len(wf['steps'])}):")
            for s in wf["steps"]:
                dep_str = (
                    f" (Depends: {', '.join(s['depends_on'])})"
                    if s["depends_on"]
                    else ""
                )
                print(
                    f"      * Step {s['step']}: [{s['component']}] -> {s['description']}{dep_str}"
                )
        print()


def handle_validate_flow(args):
    """Orchestrate the validation command execution."""
    path = Path(args.path)
    print_premium(f"🧐 Validating workflow skill at {path}...", BOLD + BLUE)

    parsed = parse_workflow_skill(path)
    if not parsed:
        print_premium("❌ Failed to parse workflow file.", RED)
        sys.exit(1)

    is_valid, errors = validate_steps_dag(parsed["steps"])
    if is_valid:
        print_premium(
            "✅ Workflow passes topological DAG checks! No circular dependencies.",
            GREEN,
        )
    else:
        print_premium("❌ Circular dependencies or broken references detected:", RED)
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


def handle_query_kg_flow(args):
    """Orchestrate querying the local SQLite database."""
    db_path = (
        Path(args.db)
        if args.db
        else Path("/home/apps/workspace/knowledge_graph_test.db")
    )
    query_local_kg(db_path)


def main():
    parser = argparse.ArgumentParser(description="Skill Workflow Builder CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List command
    list_parser = subparsers.add_parser("list", help="List all current workflows")
    list_parser.add_argument("--root", help="Custom path to the workflows directory")

    # Scaffold command
    scaffold_parser = subparsers.add_parser(
        "scaffold", help="Scaffold a new workflow skill"
    )
    scaffold_parser.add_argument("name", help="Name of the workflow (e.g. check_disk)")
    scaffold_parser.add_argument(
        "--domain", required=True, help="Domain directory (e.g. infra)"
    )
    scaffold_parser.add_argument(
        "--description", required=True, help="High level description"
    )
    scaffold_parser.add_argument("--tags", help="Comma-separated tags list")
    scaffold_parser.add_argument(
        "--requires", help="Comma-separated required tools list"
    )
    scaffold_parser.add_argument(
        "--root", help="Custom path to the workflows directory"
    )
    scaffold_parser.add_argument(
        "--interactive", action="store_true", help="Interactively enter step details"
    )
    scaffold_parser.add_argument(
        "--steps-json", help="JSON string representing workflow steps"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a workflow file")
    validate_parser.add_argument("path", help="Path to SKILL.md of the workflow")

    # Query local KG command
    query_parser = subparsers.add_parser(
        "query-kg", help="Query local Knowledge Graph SQLite"
    )
    query_parser.add_argument("--db", help="Path to the database file")

    args = parser.parse_args()

    if args.command == "list":
        handle_list_flow(args)
    elif args.command == "scaffold":
        handle_scaffold_flow(args)
    elif args.command == "validate":
        handle_validate_flow(args)
    elif args.command == "query-kg":
        handle_query_kg_flow(args)


if __name__ == "__main__":
    main()
