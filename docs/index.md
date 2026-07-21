# Universal Skills

Universal Skills is a catalog of reusable agent capabilities. Atomic skills describe
one capability; skill workflows contain only a dependency graph that composes atomic
skills or exact MCP tools.

The catalog is intentionally split by ownership:

- Cross-platform capabilities live under `universal_skills/<domain>/`.
- Ordered or parallel compositions live under
  `universal_skills/<domain>-workflows/`.
- Platform and package operations live with their provider under
  `agent-packages/agents/<package>/<module>/skills/` and are discovered through the
  `agent_utilities.skill_providers` entry-point group.

This prevents a universal skill from quietly depending on one deployment, service,
or private filesystem layout.

## Catalog review

The catalog has a checked-in, reproducible structural review:

- [Skill catalog audit](skill-catalog-audit.md) lists every canonical skill and its
  current structural or routing findings.
- [Improvement roadmap](skill-catalog-improvement-roadmap.md) explains category-level
  priorities, missing capabilities, package ownership, and proposed pure workflows.
- [Architecture overview](overview.md) defines the skill and workflow contracts.

Run the same audit locally:

```bash
python universal_skills/agent-tools/skill-catalog-auditor/scripts/audit_catalog.py \
  universal_skills --format markdown
```

The audit excludes nested `assets/` templates and generated `skill_graphs/`; those
are package resources rather than installable catalog entries.

## Install

```bash
pip install universal-skills
install-skills --all-detected --symlink
```

For an editable checkout:

```bash
pip install -e '.[test]'
install-skills --all-detected --symlink
```

## Authoring

Use `skill-builder` for one atomic capability and `skill-workflow-builder` for a
pure DAG. Before proposing a change, run:

```bash
python scripts/check_atomicity.py --strict
pytest -q tests/test_workflows_compile.py
pre-commit run --all-files
```

The builders reject stale paths and generate only the resources explicitly requested.
