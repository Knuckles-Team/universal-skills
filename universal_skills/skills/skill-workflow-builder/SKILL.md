---
name: skill-workflow-builder
domain: agent-tools
skill_type: skill
description: >-
  Scaffold and validate a dependency-ordered workflow that only groups existing
  atomic skills or explicitly named MCP tools. Use when creating or repairing a
  dual-mode workflow in a universal_skills domain ending in -workflows, with a
  matching DAG, team configuration, native execution waves, and arbora delegation.
  Do not use to author an atomic skill or to embed business logic in workflow steps.
license: MIT
tags: [workflow, scaffolding, dag, validation, atomicity]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Skill Workflow Builder

Create pure compositions under
`universal_skills/<domain>-workflows/<workflow-name>/`. Implement business logic
inside atomic skills; each workflow node may bind to exactly one existing atomic
skill or one explicit MCP tool.

## Define the DAG

Supply steps as a JSON list. Use `skill` for a catalog skill or `mcp_tool` for a
single MCP tool. Never provide both. `id` is optional and gives the node a unique
kebab-case identifier; otherwise the builder derives it from the binding.
Dependencies may name an earlier node or use `Step N`.

For a package-owned skill that is not present in the local universal catalog, add
`package` to that node and name the same distribution in the workflow's `requires`
frontmatter through `--requires`. This preserves exact ownership without treating an
arbitrary unresolved name as an atomic skill.

```json
[
  {
    "step": 1,
    "skill": "speckit-specify",
    "agent": "planning-specialist",
    "depends_on": []
  },
  {
    "step": 2,
    "skill": "scholarx-operations",
    "package": "scholarx",
    "agent": "research-specialist",
    "depends_on": ["speckit-specify"]
  }
]
```

Do not add descriptions, prompts, expected-output prose, shell commands, or other
inline logic to a step. Make every node identifier and specialist identifier unique
and kebab-case. The builder rejects missing or unowned skills, ambiguous bindings,
multiple MCP tools in one node, broken dependencies, and cycles.

## Scaffold

Run from the repository root and pass a trigger-complete description:

```bash
python universal_skills/skills/skill-workflow-builder/scripts/build_workflow.py \
  scaffold issue-planning \
  --domain development-workflows \
  --description "Plan a repository issue through specification and task decomposition. Use when the user asks to turn an existing issue into an implementation-ready plan." \
  --steps-json '[{"step":1,"skill":"speckit-specify","agent":"planning-specialist","depends_on":[]},{"step":2,"skill":"speckit-tasks","agent":"planning-specialist","depends_on":["speckit-specify"]}]'
```

The builder writes:

- workflow frontmatter with `skill_type: workflow` and a complete `team_config`;
- a pure `### Step N:` dependency DAG;
- `references/team.yaml` matching the frontmatter team configuration exactly;
- a generated `## Execution` section whose waves match the DAG; and
- the standard arbora delegation footer.

Use `--root <path-to-universal_skills>` for another checkout. Use `--interactive`
instead of `--steps-json` to collect bindings without inline step prose.

## Steps

1. Write the DAG as a JSON list of `skill` or `mcp_tool` nodes and list the available catalog skills with `ls universal_skills/skills | grep -c .`. Verify that every `skill` name you plan to use appears under `universal_skills/skills/`.
2. Scaffold the workflow with `python universal_skills/skills/skill-workflow-builder/scripts/build_workflow.py scaffold <name> --domain <domain>-workflows --description "<trigger-complete text>" --steps-json '<json>'`. Verify that the command exits 0 and creates `universal_skills/<domain>-workflows/<name>/SKILL.md`.
3. Check the generated team file with `cat universal_skills/<domain>-workflows/<name>/references/team.yaml`. Verify that it exists and names every specialist used in the DAG.
4. Validate with `python universal_skills/skills/skill-workflow-builder/scripts/build_workflow.py validate universal_skills/<domain>-workflows/<name>/SKILL.md`. Verify that it reports no missing bindings, broken dependencies or cycles.
5. Inspect existing workflows with `python universal_skills/skills/skill-workflow-builder/scripts/build_workflow.py list`. Verify that the new workflow is listed with its domain and step count.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Builder rejects a node as unowned or missing | The `skill` name is not in the local catalog and has no `package` | Correct the name against `ls universal_skills/skills`, or add `package` and pass `--requires <distribution>` |
| Ambiguous binding error | A node sets both `skill` and `mcp_tool` | Remove one key so each node binds exactly one target |
| Cycle or broken dependency reported | `depends_on` names a later or unknown node | Rewrite `depends_on` to earlier node ids or `Step N` references and rerun `validate` |
| `validate` reports team.yaml mismatch | The frontmatter team configuration was edited by hand | Delete the edit and regenerate with `scaffold`, or copy the frontmatter `team_config` into `references/team.yaml` exactly |

## Validate

Validate both generated layers and every binding:

```bash
python universal_skills/skills/skill-workflow-builder/scripts/build_workflow.py \
  validate universal_skills/development-workflows/issue-planning/SKILL.md
```

Use `list` to inspect workflow metadata without changing files. After adding an
in-repository workflow, update release tracking and run the repository atomicity,
workflow compiler, frontmatter-portability, and path-portability checks.
