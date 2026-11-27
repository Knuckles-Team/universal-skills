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
  version: '1.7.0'
  author: Knuckles-Team
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

## Steps

1. Decide that the capability is one atomic skill and pick a kebab-case name of at most 64 characters. Verify with `ls universal_skills/*/<name>` that the name is not already taken.
2. Scaffold with `python universal_skills/skills/skill-builder/scripts/init_skill.py <name> --path universal_skills/<domain> --description "<what it does. Use when ...>" --resources references`. Verify that `ls universal_skills/<domain>/<name>` shows `SKILL.md` and only the requested resource folders.
3. Replace the generated instruction with the minimal domain procedure, and add scripts only for fragile operations. Verify that `grep -rn "TOD[O]\|depends_on\|### Step" universal_skills/<domain>/<name>` prints nothing.
4. Package with `python universal_skills/skills/skill-builder/scripts/package_skill.py universal_skills/<domain>/<name> dist`. Verify that `ls dist` shows the new `.skill` archive and that the packager reported no validation errors.
5. Run the repository atomicity and portability checks, for example `python scripts/check_atomicity.py --strict`. Verify that they exit 0.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `init_skill.py` rejects the `--path` | The path points at a workflow domain or a nested folder | Use a direct child of `universal_skills` that is not a `-workflows` domain, or build a workflow with `skill-workflow-builder` |
| Packager rejects the skill | It holds workflow metadata, DAG headings, placeholders, symlinks or files like `.env` | Remove the offending items named in the error and package again |
| Description fails validation | It is over 1024 characters, has angle brackets, or lacks `Use when` | Rewrite it to state what the skill does and an explicit `Use when` trigger without `<` or `>` |
| The skill keeps growing steps for several capabilities | It is a composition, not an atomic skill | Split it, and move the ordered composition to a `<domain>-workflows` skill |

## Scaffold an atomic skill

Run the initializer from the repository root. Point `--path` at one direct child
of `universal_skills`; workflow domains are rejected.

```bash
python universal_skills/skills/skill-builder/scripts/init_skill.py report-summarizer \
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
python universal_skills/skills/skill-builder/scripts/package_skill.py \
  universal_skills/docs/report-summarizer dist
```

The packager validates the atomic contract before writing a `.skill` archive. It
rejects workflow metadata, DAG syntax, placeholder markers, symlinks, invalid
routing metadata, and unsafe files such as `.env` or private keys. Run the
repository atomicity, frontmatter-portability, path-portability, and focused tests
before finalizing an in-repository skill.
