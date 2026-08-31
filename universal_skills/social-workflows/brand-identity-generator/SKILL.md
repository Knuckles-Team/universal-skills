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
  version: '1.3.1'
  author: Genius
---

# Brand Identity Generator Workflow

Compose the named atomic skills without adding trademark or legal logic here.

## Inputs

Provide the brand name, mission/positioning, target audience, and any existing
visual constraints.

## Steps

### Step 0: brand-guidelines [skill: brand-guidelines]

Invoke `$brand-guidelines` with the workflow inputs to generate the
brand identity system.

Expected: `brand_identity_system`

### Step 1: canvas-design [skill: canvas-design] [depends_on: Step 0]

Invoke `$canvas-design` with `brand_identity_system` to render
matching visual asset mockups.

Expected: `brand_asset_mockups`

## Output

Return `brand_identity_system` and `brand_asset_mockups`. Does not publish or
register any trademark.

## Execution

- **Run first:** Step 0 — `$brand-guidelines`.
- **After level 0:** Step 1 — `$canvas-design`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
