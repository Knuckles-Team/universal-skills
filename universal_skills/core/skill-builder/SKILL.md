---
name: skill-builder
domain: core
skill_type: skill
description: >-
  Scaffold and package one atomic skill in the universal-skills catalog with
  valid routing metadata and only the resource directories it needs. Use when
  creating a new reusable capability or repairing the structure of an existing
  atomic skill. Do not use for ordered or parallel compositions of multiple
  capabilities; use skill-workflow-builder instead.
license: MIT
tags: [skills, scaffolding, validation, atomicity]
metadata:
  version: '1.2.1'
  author: Genius
---

# Skill Builder

Create one self-contained capability under `universal_skills/<domain>/<skill-name>/`.
Keep its trigger surface narrow enough that one user intent selects the whole skill.

## Preserve atomicity

- Give the skill one purpose and one primary capability.
- Keep ordered or parallel composition out of an atomic `SKILL.md`; do not add
  `### Step N:` DAG headings, `depends_on`, `team_config`, or specialist blocks.
- Move a composition of independently useful skills to a `<domain>-workflows`
  directory with `skill-workflow-builder`.
- Keep package-owned behavior in the owning agent package rather than making it
  universal.

Read [references/workflows.md](references/workflows.md) when the boundary between
one procedure and a multi-skill workflow is unclear. Read
[references/output-patterns.md](references/output-patterns.md) only when the skill
needs a stable output format.

## Scaffold an atomic skill

Run the initializer from the repository root. Point `--path` at one direct child
of `universal_skills`; workflow domains are rejected.

```bash
python universal_skills/core/skill-builder/scripts/init_skill.py report-summarizer \
  --path universal_skills/docs \
  --description "Summarize one report into a concise evidence-backed brief. Use when the user supplies a report and asks for its findings or recommendations." \
  --resources references
```

Use a kebab-case name of at most 64 characters. Make the description self-sufficient:
state what the capability does, include an explicit `Use when` trigger, keep it at
most 1024 characters, and avoid angle brackets. Request only the comma-separated
resource directories the skill will actually use: `scripts`, `references`, or
`assets`. With no `--resources`, the initializer creates only `SKILL.md`.

## Complete and verify the skill

Replace the generated generic instruction with the minimum domain procedure the
agent cannot infer. Add deterministic scripts only for fragile or repeatedly
rewritten operations, and tell the agent exactly when to read each reference.

Package only after the skill is complete:

```bash
python universal_skills/core/skill-builder/scripts/package_skill.py \
  universal_skills/docs/report-summarizer dist
```

The packager validates the atomic contract before writing a `.skill` archive. It
rejects workflow metadata, DAG syntax, placeholder markers, symlinks, invalid
routing metadata, and unsafe files such as `.env` or private keys. Run the
repository atomicity, frontmatter-portability, path-portability, and focused tests
before finalizing an in-repository skill.
