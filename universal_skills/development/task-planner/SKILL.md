---
name: task-planner
domain: development
skill_type: skill
description: >-
  Generate Spec Kit tasks.md for one tracked specs/<stable-id>/ feature, with
  requirement, design, test, quality, ledger, and repository dependencies.
license: MIT
tags: [planner, sdd]
metadata:
  version: '1.3.2'
  author: Genius
---

# SDD Task Planner

Plan executable implementation tasks for one feature in `specs/<stable-id>/tasks.md`. Read its `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` where present, plus `.specify/memory/constitution.md`. If `plan.md` or essential design decisions are missing, report that prerequisite instead of inventing a plan. Use the resolved GitHub Spec Kit tasks template and its phase, story, task ID, and `[P]` conventions. Feature artifacts belong in tracked repository-root `specs/`, never `.specify/specs/` or `agent_data/specs/`.

Favor independently verifiable vertical slices. Give each task a stable ID, a specific file path, requirement and acceptance IDs, prerequisites, expected verification, and owning repository. Use `[P]` only when tasks have no dependency or file collision and can run safely in parallel. Cross-repository work gets local tasks in each owning repository with explicit contract and related-spec links. Use graph-os impact/code context when available to identify downstream obligations; report unavailable lookups rather than assuming no impact.

Include tasks to reuse or extend named existing wiring, implement the documented interface and data flow, add positive and negative tests at the right level, verify the runtime path, and update affected docs. Include explicit applicable CCCC, `jscpd`, Dupehound, and KISS review gates, using configured thresholds. Missing tool configuration becomes a setup or decision task, never a claimed pass. Add a final evidence task that reconciles linked ledger IDs against merged code, tests, and documentation; planning alone does not close a ledger item.

Write only the feature's `tasks.md` and any necessary task references. Preserve IDs already used by contributors when revising the task list. Sync changed files to the KG if available, with Git files remaining the authority. Issue tracker publication is optional and requires user authorization.
