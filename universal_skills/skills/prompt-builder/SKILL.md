---
name: prompt-builder
domain: agent-tools
skill_type: skill
description: >-
  Author and validate canonical system-prompt JSON blueprints for meristem agents and agent-packages. Use when creating or fixing a main_agent.json / a prompts directory JSON system prompt, when an agent-package needs its system prompt, or when a prompt must conform to the StructuredPrompt canonical schema. Do NOT use for content-generation templates or for authoring skills (use skill-builder).
license: MIT
tags: [prompts, system-prompt, agent, builder, structured-prompt, json]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Prompt Builder

Scope: Author and validate canonical system-prompt JSON blueprints for meristem agents and agent-packages. Use when creating or fixing a main_agent.json / a prompts directory JSON system prompt, when an agent-package needs its system prompt, or when a prompt must conform to the StructuredPrompt canonical schema. Produces schema-valid blueprints with the body in instructions.core_directive plus schema_version/source/skills/tools, and validates them against the one shared validator (validate_canonical). Do NOT use for content-generation templates or for authoring skills (use skill-builder).

Authors and validates **canonical system-prompt JSON blueprints** — the
`StructuredPrompt` format (CONCEPT:MERISTEM-ORCH.routing.resolve-body-single-canonical) that meristem ingests into
the Knowledge Graph prompt library and that every agent-package ships as its
`prompts/main_agent.json`.

The canonical schema is **owned by the Pydantic model**
`meristem.prompting.structured.StructuredPrompt` — this skill is a thin,
drift-free front-end over it. The machine-readable JSON Schema is generated at
`meristem/prompting/prompt.schema.json` (via `scripts/gen_prompt_schema.py`).

## The canonical contract (what a valid prompt MUST have)

- `schema_version` — `"1.0"` (the canonical schema version).
- `task` — a stable slug/identifier (e.g. `"gitlab-agent"`).
- `type` — must be `"prompt"`.
- `source` — provenance / KG namespace (e.g. `"gitlab-api"` or `"meristem:base"`).
- **Body** in `instructions.core_directive` (the ONE canonical body location).
  Legacy top-level `content`/`input` are migration-only — never author them.

Optional but standardized: `metadata` (description/topic/tone/style/audience),
`identity` (role/goal/personality), the rest of `instructions`
(responsibilities/capabilities/workflow/quality_checklist), `engineering_rules`,
`rules`, `skills` (skill slugs the prompt expects installed), `tools`, and the
composition fields `extends` (e.g. `"meristem:base"`) + `compose`
(`append` | `prepend` | `replace`).

## Build a prompt

```bash
python scripts/build_prompt.py \
  --task gitlab-agent --source gitlab-api \
  --role "GitLab Platform Engineer" \
  --directive "You are the GitLab agent. Use the gitlab MCP tools to manage projects, MRs, and pipelines. Verify before mutating." \
  --skills gitlab-mr-publisher --tools workspace-manager,agent-workflows \
  --extends meristem:base \
  -o /path/to/pkg/prompts/main_agent.json
```

Or scaffold a placeholder skeleton to fill in: `python scripts/build_prompt.py
--task my-agent --source my-pkg --scaffold -o prompts/main_agent.json`.

## Validate a prompt

```bash
python scripts/validate_prompt.py prompts/main_agent.json
```

The validator fails on any non-canonical field. It is the same
`validate_canonical` used by the CI gate (`check_prompt_schema.py`) and
per-package `test_prompt_parity.py`, so "valid here" means "valid in CI".

## Steps

1. Choose the `task` slug, `source` namespace, role and directive for the agent. Verify that `ls scripts/` shows `build_prompt.py` and `validate_prompt.py`.
2. Generate the blueprint with `python scripts/build_prompt.py --task <slug> --source <source> --directive "<text>" -o prompts/main_agent.json`. Verify that the output file exists and holds `instructions.core_directive`.
3. Validate it with `python scripts/validate_prompt.py prompts/main_agent.json`. Verify that the validator exits with status 0.
4. Check the contract fields with `grep -n '"schema_version"\|"type"' prompts/main_agent.json`. Verify that `schema_version` is `1.0` and `type` is `prompt`.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| ImportError for `meristem` | The package is not installed | Run `pip install meristem` and rerun the script |
| Validator rejects top-level `content` or `input` | Legacy fields were authored | Move the body into `instructions.core_directive` and delete the legacy fields |
| Placeholder text remains after `--scaffold` | Skeleton was not filled in | Replace every placeholder value and revalidate |

## Notes

- Both scripts guard the `meristem` import and print an install hint if
  it is missing (`pip install meristem`).
- A package contributes its prompt to the KG library by declaring a
  `[project.entry-points."scion_sdk.connector"]` entry point and
  placing it in the package's `prompts/` directory (see `mcp-builder`).
- For per-agent overrides without editing the package, drop a `*.json` into the
  XDG overlay `~/.config/arbora/prompts/`.
