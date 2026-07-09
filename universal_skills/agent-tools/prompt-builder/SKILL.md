---
name: prompt-builder
domain: agent-tools
skill_type: skill
description: >-
  Author and validate canonical system-prompt JSON blueprints for agent-utilities
  agents and agent-packages. Use when creating or fixing a main_agent.json / a
  prompts/*.json system prompt, when an agent-package needs its system prompt, or
  when a prompt must conform to the StructuredPrompt canonical schema. Produces
  schema-valid blueprints with the body in instructions.core_directive plus
  schema_version/source/skills/tools, and validates them against the one shared
  validator (validate_canonical). Do NOT use for content-generation templates or
  for authoring skills (use skill-builder).
license: MIT
tags: [prompts, system-prompt, agent, builder, structured-prompt, json]
metadata:
  version: '1.1.0'
  author: Genius
---

# Prompt Builder

Authors and validates **canonical system-prompt JSON blueprints** — the
`StructuredPrompt` format (CONCEPT:AU-ORCH.routing.resolve-body-single-canonical) that agent-utilities ingests into
the Knowledge Graph prompt library and that every agent-package ships as its
`prompts/main_agent.json`.

The canonical schema is **owned by the Pydantic model**
`agent_utilities.prompting.structured.StructuredPrompt` — this skill is a thin,
drift-free front-end over it. The machine-readable JSON Schema is generated at
`agent_utilities/prompting/prompt.schema.json` (via `scripts/gen_prompt_schema.py`).

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

## Build a prompt

```bash
python scripts/build_prompt.py \
  --task gitlab-agent --source gitlab-api \
  --role "GitLab Platform Engineer" \
  --directive "You are the GitLab agent. Use the gitlab MCP tools to manage projects, MRs, and pipelines. Verify before mutating." \
  --skills gitlab-mr-publisher --tools workspace-manager,agent-workflows \
  --extends agent-utilities:base \
  -o /path/to/pkg/prompts/main_agent.json
```

Or scaffold a placeholder skeleton to fill in: `python scripts/build_prompt.py
--task my-agent --source my-pkg --scaffold -o prompts/main_agent.json`.

## Validate a prompt

```bash
python scripts/validate_prompt.py prompts/main_agent.json --strict
```

`--strict` fails on any legacy `content`/`input` key and any non-canonical
field; without it, those are warnings. This is the same `validate_canonical`
the CI gate (`check_prompt_schema.py`) and per-package `test_prompt_parity.py`
use, so "valid here" means "valid in CI".

## Notes

- Both scripts guard the `agent_utilities` import and print an install hint if
  it is missing (`pip install agent-utilities`).
- A package contributes its prompt to the KG library by declaring a
  `[project.entry-points."agent_utilities.prompt_providers"]` entry pointing at
  its `prompts` subpackage (see `agent-package-builder`).
- For per-agent overrides without editing the package, drop a `*.json` into the
  XDG overlay `~/.config/agent-utilities/prompts/`.
