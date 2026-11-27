---
name: brand-identity-generator
skill_type: workflow
description: >-
  Generate a comprehensive brand identity system (logo concepts, color palette,
  typography scale, imagery direction, voice/tone) and render matching visual
  asset mockups. Use when establishing a new brand or evolving an existing one;
  this workflow does not publish or register any trademark.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: brand-identity-generator-team
  task_pattern: brand identity system and visual mockup generation
  execution_mode: sequential
  specialist_ids:
    - brand-guidelines
    - canvas-design
tags: [social, branding, design]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Brand Identity Generator Workflow

Compose the named atomic skills without adding trademark or legal logic here.

## Inputs

Provide the brand name, mission/positioning, target audience, and any existing
visual constraints.

## Steps

1. Collect the brand name, mission, target audience and visual constraints from the caller into one inputs file such as `brand-inputs.md`. Verify that all four inputs are written down before any skill runs.
2. Generate the brand identity system with the `brand-guidelines` skill (Step 0). Verify that `brand_identity_system` covers the brand name, positioning, audience and visual rules.
3. Render matching visual asset mockups with the `canvas-design` skill from `brand_identity_system` (Step 1). Verify that `brand_asset_mockups` lists at least one asset and that `ls` shows the rendered files.

### Step 0: brand-guidelines [skill: brand-guidelines]

Invoke `$brand-guidelines` with the workflow inputs to generate the
brand identity system.

Expected: `brand_identity_system`

### Step 1: canvas-design [skill: canvas-design] [depends_on: Step 0]

Invoke `$canvas-design` with `brand_identity_system` to render
matching visual asset mockups.

Expected: `brand_asset_mockups`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `brand_identity_system` is generic | The mission or audience input was vague | Ask the caller for a concrete positioning statement and target audience, and rerun the `brand-guidelines` skill |
| Mockups ignore the identity rules | `canvas-design` ran without `brand_identity_system` | Pass the full `brand_identity_system` output into Step 1 and render again |
| No mockup files are listed | The render step wrote to a different directory | Check the output path reported by `canvas-design` and move the files to the expected location |


## Output

Return `brand_identity_system` and `brand_asset_mockups`. Does not publish or
register any trademark.

## Execution

- **Run first:** Step 0 — `$brand-guidelines`.
- **After level 0:** Step 1 — `$canvas-design`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
