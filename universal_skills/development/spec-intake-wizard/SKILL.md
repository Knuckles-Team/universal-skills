---
name: spec-intake-wizard
skill_type: skill
description: >
  Interactive Spec Intake Wizard atomic skill. Prompts the user with structured
  fields, clarifies ambiguity, validates inputs, and outputs parsed JSON parameters.
domain: development
license: MIT
tags: [sdd, user-interaction, wizard, specification, planning]
metadata:
  version: '1.1.0'
  author: Genius
requires: []
---

# SDD Spec Intake Wizard Skill

Stateless atomic operation to engage the user in a high-fidelity, interactive intake flow. It prompts the user for essential system parameters, recommends baseline defaults to expedite answers, validates constraints in real time, and outputs a normalized JSON metadata structure that feeds downstream specification generators (`spec-generator`) and planners (`task-planner`).

## Role & Goal
- **Role**: Technical Product Manager / Interactive Intake Engine.
- **Goal**: Gather high-fidelity, unambiguous requirements from the user with zero friction.

## Steps

### Step 1: initialize_wizard_schema
Initialize the interactive session with a dynamic schema based on the targeted domain or feature category:
- Define the standard template of required fields:
  - `feature_name`: String (required, 2-100 characters)
  - `target_domain`: String (e.g. "infra", "finance", "dev-workflows", "ops", "research")
  - `high_level_goal`: String (required, summary of intent)
  - `key_constraints`: List of strings (e.g. "latency < 200ms", "no external databases")
  - `expected_inputs`: List of fields and types
  - `expected_outputs`: List of fields and types
- Populate a set of smart defaults and "recommended" answers to enable a single-click or empty-input acceptance.
- Output parameters:
  - `session_schema`: The formulated validation schema and prompt rules.

### Step 2: run_clarification_loop [depends_on: initialize_wizard_schema]
Interact with the user to collect parameters and resolve the top ambiguity gaps:
- Present the structured questions sequentially or as a single clear interactive prompt.
- For each option, clearly present the recommended default (e.g., "[Default: YES]" or "[Default: patch]").
- Allow the user to input custom values, accept defaults by hitting Enter, or skip the remaining loop by typing "skip".
- Gracefully handle empty or invalid entries with supportive inline validation help messages.
- Output parameters:
  - `raw_answers`: Key-value map of collected user responses.

### Step 3: compile_validated_intake [depends_on: run_clarification_loop]
Execute final validation, reconcile inputs against the target default schema, and produce a unified JSON configuration:
- Merge `raw_answers` with `session_schema` defaults for any omitted or skipped fields.
- Assert strict structural validation constraints (e.g., ensure mandatory keys are present and data types match).
- Parse constraints and requirements into a normalized data model structure:
  - `metadata`: `{ created_at: String, user: String, skip_flag: Boolean }`
  - `spec_intake`: `{ name: String, domain: String, goal: String, constraints: List, data_flow: Object }`
- Output parameters:
  - `status`: "SUCCESS" or "FAILED"
  - `payload`: Standardized JSON representation of the user requirements.
  - `summary_markdown`: A clean, structured markdown table representing the chosen configuration parameters.
