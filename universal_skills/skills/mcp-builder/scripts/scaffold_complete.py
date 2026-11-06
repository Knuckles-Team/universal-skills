"""Complete an existing connector repository (US-MCP-BUILDER-R011.17).

    python3 scaffold_connector.py complete /path/to/connector-repo

The mode adds only what is missing and never overwrites a file. It adds a
prompt, one skill per tool domain, an ontology file whose classes extend a
core class, and ``<pkg>/connector_contracts.py``. It prints, and never
applies, a removal suggestion for each ``owl:imports`` of the core ontology.
The report is deterministic: sorted lines, no date, user or host name.
"""

from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

CORE_IRI = "http://knuckles.team/kg"
ENTRY_POINT_GROUP = "scion_sdk.connector"
_SUFFIXES = ("-mcp", "-api", "-agent", "-server")
_READ_PREFIXES = ("get", "list", "search", "read", "find", "query", "fetch")
_BASE_CLASS_WORDS = ("Base", "Auth", "Session", "Transport", "Http", "Error", "Exception")


def _identity(repo: Path) -> tuple[str, str]:
    """The fleet name and the package name the connector entry point declares."""
    project = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    group = project.get("project", {}).get("entry-points", {}).get(ENTRY_POINT_GROUP, {})
    if len(group) != 1:
        raise SystemExit(f"{repo}: pyproject.toml must declare one {ENTRY_POINT_GROUP} entry point")
    fleet, value = next(iter(group.items()))
    return fleet, str(value).split(":", 1)[0].split(".", 1)[0]


def _short(fleet: str) -> str:
    for suffix in _SUFFIXES:
        if fleet.endswith(suffix):
            return fleet.removesuffix(suffix)
    return fleet


def _domain(class_name: str) -> str:
    name = re.sub(r"(Api|API|Client|Mixin)", "", class_name) or "operations"
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def _api_classes(pkg_dir: Path) -> list[tuple[str, list[ast.FunctionDef]]]:
    """Each API client class with its public methods, in file and source order."""
    files = sorted(pkg_dir.glob("api_client*.py")) + sorted(pkg_dir.glob("api/*.py"))
    found: list[tuple[str, list[ast.FunctionDef]]] = []
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or any(w in node.name for w in _BASE_CLASS_WORDS):
                continue
            methods = [
                f for f in node.body
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and not f.name.startswith("_")
            ]
            if methods:
                found.append((node.name, methods))
    return found


def _domains(pkg_dir: Path, prefix: str) -> dict[str, list[tuple[str, tuple[str, ...]]]]:
    """Tool domain -> [(served tool name, parameter names)]. One domain per client class."""
    out: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
    for class_name, methods in _api_classes(pkg_dir):
        tools = out.setdefault(_domain(class_name), [])
        for method in methods:
            params = tuple(a.arg for a in method.args.args if a.arg != "self")
            tools.append((f"{prefix}_{method.name}", params))
    if len(out) > 1 and "" in out:
        out.pop("")
    return out


def _tuple(values: list[str] | tuple[str, ...]) -> str:
    inner = ", ".join(json.dumps(v) for v in values)
    return f"({inner},)" if len(values) == 1 else f"({inner})"


def _source_locations(pkg_dir: Path, url_env: str | None) -> list[dict[str, str]]:
    """Data locations derived from declared ``source_meta`` sources, literals only."""
    path = pkg_dir / "connector_sources.py"
    if not path.is_file():
        return []
    locations = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", "")) == "source_meta"):
            continue
        args = {k.arg: k.value.value for k in node.keywords if isinstance(k.value, ast.Constant)}
        if {"tool", "source_id", "ontology_class"} <= set(args) and url_env:
            locations.append({"name": args["source_id"], "holds": args["ontology_class"], "tool": args["tool"]})
    return locations


def _url_env(pkg_dir: Path) -> str | None:
    for path in sorted(pkg_dir.rglob("*.py")):
        match = re.search(r'url_env\s*=\s*"([A-Z0-9_]+)"', path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return None


def _static_contracts(
    short: str,
    domains: dict[str, list[tuple[str, tuple[str, ...]]]],
    prompts: list[str],
    skills: dict[str, str],
    locations: list[dict[str, str]],
    url_env: str | None,
    agents: list[dict] | None = None,
) -> tuple[str, list[str]]:
    """The contracts module from the static Api method list, and the parts a human must finish."""
    human: list[str] = []
    contracts, links = [], []
    for domain, tools in sorted(domains.items()):
        task = f"{short}-{domain}"
        steps = "\n".join(
            f"            ToolStep(tool={json.dumps(tool)}, params={_tuple(params) if params else '()'}),"
            for tool, params in tools
        )
        contracts.append(
            f"    ToolUseContract(\n        task={json.dumps(task)},\n        steps=(\n{steps}\n        ),\n    ),"
        )
        skill = skills.get(domain)
        links.append(
            f"    SurfaceLink(\n        task={json.dumps(task)},\n        tools={_tuple([t for t, _ in tools])},\n"
            f"        prompts={_tuple(prompts) if prompts and not agents else '()'},\n"
            f"        skills={_tuple([skill]) if skill else '()'},\n    ),"
        )
        human.append(f"contract {task}: order the steps, add result fields and refusals")
    roles = []
    for agent in agents or []:
        links.append(
            f"    SurfaceLink(\n        task={json.dumps(agent['task'])},\n        tools={_tuple(agent['tools'])},\n"
            f"        prompts=({json.dumps(agent['prompt'])},),\n        skills={_tuple(agent['skills']) if agent['skills'] else '()'},\n    ),"
        )
        if agent.get("business_role"):
            roles.append(
                f"    BusinessRole(\n        name={json.dumps(agent['business_role'])},\n"
                f"        tasks=({json.dumps(agent['task'])},),\n    ),"
            )
    if not roles:
        human.append("business roles: declare a BusinessRole and its prompt for each role the connector serves")
    loc_lines = [
        f"    DataLocation(\n        name={json.dumps(loc['name'])},\n        holds=({json.dumps(loc['holds'])},),\n"
        f"        instance={json.dumps(url_env)},\n        read_tool={json.dumps(loc['tool'])},\n    ),"
        for loc in locations
    ]
    if not loc_lines:
        human.append("data locations: declare which instance or store holds each ontology class")
    text = (
        '"""Tool-use contracts, surface links and data locations of this connector.\n\n'
        "Completed from the static Api method list. Every argument is a literal.\n"
        '"""\n\n'
        "from scion_sdk.surface_contracts import (\n    BusinessRole,\n    DataLocation,\n    Refusal,\n    SurfaceLink,\n    ToolStep,\n    ToolUseContract,\n)\n\n"
        "CONTRACTS = (\n" + "\n".join(contracts) + "\n)\n\n"
        "LINKS = (\n" + "\n".join(links) + "\n)\n\n"
        "LOCATIONS = (\n" + "\n".join(loc_lines) + ("\n" if loc_lines else "") + ")\n\n"
        "ROLES = (\n" + "\n".join(roles) + ("\n" if roles else "") + ")\n\n"
        "__all__ = [\"CONTRACTS\", \"LINKS\", \"LOCATIONS\", \"ROLES\", \"BusinessRole\", \"DataLocation\", "
        "\"Refusal\", \"SurfaceLink\", \"ToolStep\", \"ToolUseContract\"]\n"
    )
    return text, human


_DESTRUCTIVE = ("delete", "remove", "purge", "destroy", "drop")


def _agent_prompt(
    *, display: str, role: str, goal: str, kind: str, tools: list[str], skills: list[str],
    locations: list[str], topic: str,
) -> dict:
    """One prompt that is a complete agent definition (US-MCP-BUILDER-R011.18)."""
    destructive = [t for t in tools if any(f"_{w}" in t for w in _DESTRUCTIVE)]
    never = ["invent an id", "change data that was not read first"]
    data = (", ".join(locations) if locations else "the data the tools return")
    directive = (
        f"You are the {role}. Your goal is to {goal[0].lower() + goal[1:]} "
        f"Use the tools {', '.join(tools)}"
        + (f", guided by the skills {', '.join(skills)}. " if skills else ". ")
        + f"You read and write {data}. Read before you change. "
        + (f"Ask for approval before {', '.join(destructive)}. " if destructive else "")
        + "Never invent an id. Never change data that was not read first. "
        "Report each record you read or changed by its id, and each refusal code you receive."
    )
    agent: dict = {"kind": kind}
    if kind == "business-role":
        agent["business_role"] = role
    agent.update(
        tools=tools,
        skills=skills,
        data={"reads": locations, "writes": locations},
        guardrails={"approval_required": destructive, "never": never},
        outputs=["the id of each record read or changed", "each refusal code received"],
    )
    return {
        "title": role,
        "description": f"{'Operator' if kind == 'operator' else 'Business-role'} agent for {display}.",
        "identity": {"role": role, "goal": goal},
        "metadata": {"topic": topic},
        "prompt_version": "1",
        "instructions": {"core_directive": directive},
        "agent": agent,
    }


def _sdk_contracts(package: str) -> str | None:
    """The contracts module text from the SDK completer, when that SDK API is importable."""
    try:
        from scion_sdk.surface_contracts import complete  # type: ignore[attr-defined]
    except ImportError:
        return None
    result = complete(package)
    return result if isinstance(result, str) else None


def complete(repo: Path, templates: dict[str, str], *, use_sdk: bool = True) -> list[str]:
    """Add every missing surface file of the connector at ``repo``; return the sorted report lines."""
    fleet, package = _identity(repo)
    pkg_dir = repo / package
    short = _short(fleet)
    prefix = short.replace("-", "_")
    klass = short.replace("-", " ").title().replace(" ", "")
    display = short.replace("-", " ").title()
    fields = {
        "short": short, "short_snake": prefix, "Class": klass, "Display": display,
        "short_camel": klass[0].lower() + klass[1:], "core": templates["core"],
    }
    added: list[str] = []
    human: list[str] = []

    def write(rel: Path, text: str) -> None:
        path = pkg_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        added.append(f"added: {package}/{rel.as_posix()}")

    domains = _domains(pkg_dir, prefix)
    if not domains:
        human.append("tools: no API client class with public methods found")

    skills_dir = pkg_dir / "skills"
    existing = sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
    skills: dict[str, str] = {}
    if not existing:
        for domain, tools in sorted(domains.items()):
            name = f"{short}-{domain}"
            steps = "\n".join(f"{i}. `{tool}`" for i, (tool, _) in enumerate(tools, 1))
            write(
                Path(f"skills/{name}/SKILL.md"),
                f"---\nname: {name}\nskill_type: skill\ndomain: connector\n"
                f"description: Operate {display} {domain.replace('-', ' ')} through its MCP tools. "
                f"Use when working with {display} {domain.replace('-', ' ')}.\n---\n\n"
                f"# {display} {domain.replace('-', ' ')}\n\nRead before you change; confirm before you delete.\n\n{steps}\n",
            )
            skills[domain] = name
    else:
        for domain in domains:
            match = next((s for s in existing if s.endswith(f"-{domain}")), None)
            if match:
                skills[domain] = match

    ontology_dir = pkg_dir / "ontology"
    ttls = sorted(ontology_dir.glob("*.ttl"))
    if not ttls:
        write(Path(f"ontology/{short}.ttl"), templates["ontology"].format(**fields))
    for ttl in ttls:
        for line_no, line in enumerate(ttl.read_text(encoding="utf-8").splitlines(), 1):
            if "owl:imports" in line and CORE_IRI in line:
                human.append(
                    f"suggest: remove owl:imports of the core ontology at {package}/ontology/{ttl.name}:{line_no}"
                )

    url_env = _url_env(pkg_dir)
    locations = _source_locations(pkg_dir, url_env)
    prompts_dir = pkg_dir / "prompts"
    agents: list[dict] = []
    if not [p for p in prompts_dir.glob("*.json") if not p.name.startswith("_")] and domains:
        all_tools = [t for _, tools in sorted(domains.items()) for t, _ in tools]
        all_skills = sorted(set(skills.values()))
        names = [loc["name"] for loc in locations]
        first, first_tools = sorted(domains.items())[0]
        role_name = f"{display} {first.replace('-', ' ')} steward"
        plans = [
            dict(prompt=f"{short}-operator", role=f"{display} operator", kind="operator",
                 goal=f"Keep {display} data correct with the {display} tools.", tools=all_tools,
                 skills=all_skills, task=f"{short}-{first}"),
            dict(prompt=f"{short}-{first}-steward", role=role_name, kind="business-role",
                 goal=f"Keep {display} {first.replace('-', ' ')} records accurate.",
                 tools=[t for t, _ in first_tools], skills=[skills[first]] if first in skills else [],
                 task=f"{short}-{first}"),
        ]
        for plan in plans:
            document = _agent_prompt(
                display=display, role=plan["role"], goal=plan["goal"], kind=plan["kind"],
                tools=plan["tools"], skills=plan["skills"], locations=names, topic=short,
            )
            write(Path(f"prompts/{plan['prompt']}.json"), json.dumps(document, indent=2) + "\n")
            agents.append({**plan, "business_role": plan["role"] if plan["kind"] == "business-role" else None})
    prompts = sorted(p.stem for p in prompts_dir.glob("*.json") if not p.name.startswith("_"))
    for path in sorted(prompts_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            document = {}
        if not isinstance(document, dict) or "agent" not in document:
            human.append(f"prompt {path.stem}: add the agent definition (role, tools, skills, data, guardrails, outputs)")

    if not (pkg_dir / "connector_contracts.py").is_file() and domains:
        text = _sdk_contracts(package) if use_sdk else None
        if text is None:
            text, todo = _static_contracts(short, domains, prompts, skills, locations, url_env, agents)
            human.extend(todo)
        write(Path("connector_contracts.py"), text)

    return sorted(added) + sorted(f"needs a human: {h}" for h in human if not h.startswith("suggest:")) + sorted(
        h for h in human if h.startswith("suggest:")
    )
