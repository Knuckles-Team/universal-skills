# Universal Skills

[![PyPI version](https://img.shields.io/pypi/v/universal-skills)](https://pypi.org/project/universal-skills/)
[![Python](https://img.shields.io/pypi/pyversions/universal-skills)](https://pypi.org/project/universal-skills/)
[![License](https://img.shields.io/github/license/Knuckles-Team/universal-skills)](LICENSE)

*Version: 1.2.1*

Universal Skills is a portable catalog of agent capabilities and dependency-ordered
skill workflows. It supports Claude-compatible `SKILL.md` discovery and the
agent-utilities provider ecosystem.

## Catalog model

- `universal_skills/<domain>/<name>/` contains one atomic skill with one capability.
- `universal_skills/<domain>-workflows/<name>/` contains a pure DAG over atomic
  skills or exact MCP tools; workflows do not embed business logic.
- Platform and package operations belong under
  `agent-packages/agents/<package>/<module>/skills/` and are exposed through
  `agent_utilities.skill_providers`.
- `assets/` may contain nested templates, but those are package resources rather
  than canonical catalog entries.

The catalog includes development, infrastructure, finance, research, product,
creative, documentation, web, system, operations, content, and data capabilities.
The content and data domains include evidence-aware drafting, publication preflight,
dataset profiling, deterministic data-quality validation, and data-dictionary
authoring.

## Catalog quality and roadmap

- [Per-skill structural audit](docs/skill-catalog-audit.md)
- [Category improvement roadmap and workflow designs](docs/skill-catalog-improvement-roadmap.md)
- [Skill and workflow architecture](docs/overview.md)
- [Published documentation](https://knuckles-team.github.io/universal-skills/)

Reproduce the catalog audit locally:

```bash
python universal_skills/agent-tools/skill-catalog-auditor/scripts/audit_catalog.py \
  universal_skills --format markdown
```

The audit reports trigger quality, atomicity signals, workflow dependency problems,
unbound components, placeholder content, team-configuration drift, broken local
links, and taxonomy consistency. It is a structural lint, so safety and domain
correctness still require human review.

## Install

Install the package, then deploy discovered skills to supported agent tools:

```bash
pip install universal-skills
install-skills --all-detected --symlink
```

For local development:

```bash
git clone https://github.com/Knuckles-Team/universal-skills.git
cd universal-skills
pip install -e '.[test]'
install-skills --all-detected --symlink
```

The repository also provides `install.sh` and `install.ps1` for package installation
and skill deployment. Review targets and configuration changes before using broad
installation options.

## Use from Python

```python
from pydantic_ai_skills import SkillsToolset

from universal_skills.skill_utilities import (
    get_skill_graph_path,
    get_universal_skills_path,
)

skills = SkillsToolset(
    directories=[get_universal_skills_path(), get_skill_graph_path()]
)
```

Discovery respects each skill's enable/disable environment flag. Package-owned
skills are discovered from installed provider entry points by the universal
installer.

## Author a skill or workflow

Use the bundled builders rather than copying a legacy entry:

```bash
# Atomic skill: creates only explicitly requested resource directories
python universal_skills/core/skill-builder/scripts/init_skill.py --help

# Pure DAG workflow: resolves atomic skills or explicit MCP tools
python universal_skills/agent-tools/skill-workflow-builder/scripts/build_workflow.py --help
```

Before opening a change:

```bash
python scripts/gen_bumpversion.py
python scripts/check_atomicity.py --strict
pytest -q
pre-commit run --all-files
```

## Security boundaries

Audit and discovery are read-only. Skills that publish, send, delete, rotate,
restart, deploy, trade, persist data, or otherwise change external state must make
that side effect explicit and obtain the authorization appropriate to the target.
Network scripts must verify TLS by default, bound requests, redact secrets, and
treat retrieved content as untrusted input.

## License

MIT. See [LICENSE](LICENSE).
