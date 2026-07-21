---
name: skill-catalog-auditor
domain: agent-tools
skill_type: skill
description: >-
  Audit a skill catalog for routing quality, atomicity, workflow DAG integrity,
  placeholder content, team-config drift, broken resource links, and taxonomy
  consistency. Use when reviewing all SKILL.md files in a repository, deciding
  which skills to refine or retire, checking a catalog migration, or producing a
  complete per-skill quality report for canonical catalog entries. Use it when
  nested template assets must remain outside catalog counts. Do not use to author
  a single new skill; use skill-builder or skill-workflow-builder instead.
license: MIT
tags: [skills, audit, catalog, quality, atomicity, workflows]
metadata:
  version: '1.2.1'
  author: Genius
---

# Skill Catalog Auditor

Run a deterministic, read-only assessment across canonical `SKILL.md` files.
Bundled `assets/` templates and generated `skill_graphs/` are deliberately excluded
because they are resources, not installable catalog entries. Use the findings as
evidence for targeted edits; do not mechanically expand concise skills merely to
silence advisory checks. This is a structural lint, not a substitute for qualitative,
safety, or freshness review.

## Run the audit

From the universal-skills repository root:

```bash
python universal_skills/agent-tools/skill-catalog-auditor/scripts/audit_catalog.py \
  universal_skills
```

Use `--format json` for automation or `--format markdown --output <path>` for a
reviewable catalog report. The default exit policy fails only on structural
errors. Use `--fail-on warning` when establishing a fully clean catalog.

## Interpret findings

- Treat `error` findings as broken contracts: invalid metadata, duplicate names,
  bad DAG dependencies, missing workflow execution/team layers, placeholder-only
  workflows, or broken local links.
- Treat `warning` findings as review prompts: weak trigger descriptions, oversized
  bodies, team drift, ambiguous workflow components, or workflow-like atomic
  skills.
- Review every reported path before changing it. Some short skills are complete;
  some long skills correctly route to progressive references.

## Apply ownership rules

- Keep cross-platform, reusable atomic capabilities in `universal_skills/<domain>/`.
- Put ordered compositions in `universal_skills/<domain>-workflows/` and reference
  atomic skills or one explicit MCP tool per step.
- Put package- or platform-owned operations in that package's
  `<module>/skills/<name>/` and expose them through
  `agent_utilities.skill_providers`. Keep a universal workflow only when it
  genuinely composes capabilities across packages.

## Verify changes

Re-run the auditor, `python scripts/check_atomicity.py --strict`, the workflow
compiler tests, and the cross-agent portability checks. Regenerate
`.bumpversion.cfg` after adding or removing any `SKILL.md`.
