# Catalog architecture

## Atomic skills

An atomic skill has one trigger surface, one primary capability, and one result
contract. Its canonical location is:

```text
universal_skills/<domain>/<skill-name>/
├── SKILL.md
├── scripts/       # optional executable helpers
├── references/    # optional detailed guidance
└── assets/        # optional output resources or templates
```

`SKILL.md` frontmatter declares `name`, `domain`, `skill_type: skill`, and a
self-sufficient trigger-oriented `description`. The body explains boundaries,
inputs, outputs, safety, and only the resources needed for that capability. It does
not contain a dependency DAG or orchestrate other skills.

## Skill workflows

A workflow is a pure grouping of existing atomic skills or exact MCP tools. It owns
ordering, not business logic:

```text
universal_skills/<domain>-workflows/<workflow-name>/
├── SKILL.md
└── references/
    └── team.yaml
```

Each `### Step N:` binds one atomic skill with `[skill: <name>]` or one MCP tool
with `[mcp_tool: <server.tool>]`. `depends_on` forms an acyclic graph. The
`## Execution` section renders the same graph for native execution, while the
standard footer allows graph-os delegation. `references/team.yaml` must describe
the same specialist set and execution mode.

## Package-owned capabilities

Operations tied to one API, service, deployment, SDK, or agent package belong in
that package:

```text
agent-packages/agents/<package>/<module>/skills/<operation-skill>/SKILL.md
```

The package publishes its skill directory through the
`agent_utilities.skill_providers` setuptools entry point. A cross-package universal
workflow may invoke that skill by declaring the package and skill in `requires`.
This keeps installation, versioning, credentials, and compatibility with the owner.

## Discovery and packaging

The Python wheel includes all files below `universal_skills/`, including scripts,
references, hidden scaffold assets, and nested templates. It excludes bytecode,
caches, generated analysis results, and packaged `.skill` archives. Runtime catalog
audits count canonical `SKILL.md` entries and deliberately exclude `assets/` templates
and generated skill graphs.

## Quality gates

Use complementary checks because no one validator proves semantic quality:

```bash
# Atomic/workflow contract and version parity
python scripts/check_atomicity.py --strict
python scripts/gen_bumpversion.py --check

# Full structural and routing inventory
python universal_skills/agent-tools/skill-catalog-auditor/scripts/audit_catalog.py \
  universal_skills --fail-on never

# Executable verification
pytest -q
pre-commit run --all-files
```

The catalog auditor reports unresolved legacy composition and routing debt instead
of silently treating a passing schema check as proof that a skill is well designed.
