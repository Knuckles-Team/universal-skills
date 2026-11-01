---
name: prompt-builder
domain: agent-tools
skill_type: skill
description: >-
  Author and validate canonical system-prompt JSON blueprints for agent-utilities
  agents and agent-packages. Use when creating or fixing a main_agent.json / a
  prompts directory JSON system prompt, when an agent-package needs its system prompt, or
  when a prompt must conform to the StructuredPrompt canonical schema. Produces
  schema-valid blueprints with the body in instructions.core_directive plus
  schema_version/source/skills/tools, and validates them against the one shared
  validator (validate_canonical). Do NOT use for content-generation templates or
  for authoring skills (use skill-builder).
license: MIT
tags: [prompts, system-prompt, agent, builder, structured-prompt, json]
metadata:
  version: '1.5.2'
  author: Genius
---

# Prompt Builder

Authors and validates **canonical system-prompt JSON blueprints** — the
`StructuredPrompt` format (CONCEPT:MERISTEM-ORCH.routing.resolve-body-single-canonical) that the Knowledge Graph prompt library ingests and that every agent-package ships as its
`prompts/main_agent.json`.

The canonical schema is documented below. Its validator is tracked by
`MEDULLA-DECISION-ENGINE-R814.8`.

## The canonical contract (what a valid prompt MUST have)

- `schema_version` — `"1.0"` (the canonical schema version).
- `task` — a stable slug/identifier (e.g. `"gitlab-agent"`).
- `type` — must be `"prompt"`.
- `source` — provenance / KG namespace (e.g. `"gitlab-api"` or `"agent-utilities:base"`).
- **Body** in `instructions.core_directive` (the ONE canonical body location).
  Legacy top-level `content`/`input` are migration-only — never author them.

Optional but standardized: `metadata` (description/topic/tone/style/audience),
`identity` (role/goal/personality), the rest of `instructions`
(responsibilities/capabilities/workflow/quality_checklist), `engineering_rules`,
`rules`, `skills` (skill slugs the prompt expects installed), `tools`, and the
composition fields `extends` (e.g. `"agent-utilities:base"`) + `compose`
(`append` | `prepend` | `replace`).

## Build and validate

The builder and validator scripts are removed: the canonical schema model
(`StructuredPrompt`, `validate_canonical`) had no home after the agent-utilities
split. Author the JSON by hand to the contract above. Medulla selects packaged
system prompts as candidates (`MEDULLA-DECISION-ENGINE-R814`), and validation
of a packaged prompt against the canonical contract is filed as
`MEDULLA-DECISION-ENGINE-R814.8`.

## Notes

- A package contributes its prompt to the KG library by declaring a
  `[project.entry-points."scion_sdk.connector"]` entry point and
  placing it in the package's `prompts/` directory (see [mcp-builder](../mcp-builder/SKILL.md)).
- For per-agent overrides without editing the package, drop a `*.json` into the
  XDG overlay `~/.config/arbora/prompts/`.
