---
name: ssl-certificate-sweep
skill_type: workflow
description: >-
  Connect to a supplied set of targets, parse their TLS certificates for
  expiration and grade, and render the results as a formatted sweep report. Use
  when a fleet operator needs a recurring certificate-expiry report; this
  workflow is read-only and does not rotate or reissue certificates.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: ssl-certificate-sweep-team
  task_pattern: TLS expiry sweep and report generation
  execution_mode: sequential
  specialist_ids:
    - ssl-expiry-checker
    - document-converter
tags: [health, infrastructure, ssl, security]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.3.0'
  author: Genius
---

# SSL Certificate Sweep Workflow

Compose the named atomic skills without adding new certificate logic here.

## Inputs

Provide the target host/endpoint list.

## Steps

### Step 0: ssl-expiry-checker [skill: ssl-expiry-checker]

Invoke `$ssl-expiry-checker` with the workflow inputs to connect to
the targets and parse expiration and security grade.

Expected: `expiry_report`

### Step 1: document-converter [skill: document-converter] [depends_on: Step 0]

Invoke `$document-converter` with `expiry_report` to render it as a
formatted Markdown/PDF sweep report.

Expected: `sweep_document`

## Output

Return `expiry_report` and `sweep_document`. Does not rotate or reissue
certificates.

## Execution

- **Run first:** Step 0 — `$ssl-expiry-checker`.
- **After level 0:** Step 1 — `$document-converter`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
