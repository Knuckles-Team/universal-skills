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
  version: '1.6.0'
  author: Genius
---

# SDD Task Planner

Plan executable implementation tasks for one feature in `specs/<stable-id>/tasks.md`. Read its `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` where present, plus `.specify/memory/constitution.md`. If `plan.md` or essential design decisions are missing, report that prerequisite instead of inventing a plan. Use the resolved GitHub Spec Kit tasks template and its phase, story, task ID, and `[P]` conventions. Write each task as `- [ ] T001 [P] [US1] <ID>-R012.4 description`: the task number and the requirement row ID are required, `[P]` and `[US1]` are optional. Feature artifacts belong in tracked repository-root `specs/`, never `.specify/specs/` or `agent_data/specs/`.

Favor independently verifiable vertical slices. Give each task a stable ID, a specific file path, requirement and acceptance IDs, prerequisites, expected verification, and owning repository. Use `[P]` only when tasks have no dependency or file collision and can run safely in parallel. Cross-repository work gets local tasks in each owning repository with explicit contract and related-spec links. Use arbora impact/code context when available to identify downstream obligations; report unavailable lookups rather than assuming no impact.

Include tasks to reuse or extend named existing wiring, implement the documented interface and data flow, add positive and negative tests at the right level, verify the runtime path, and update affected docs. Include explicit applicable CCCC, `jscpd`, Dupehound, and KISS review gates, using configured thresholds. Missing tool configuration becomes a setup or decision task, never a claimed pass. Add a final evidence task that reconciles linked ledger IDs against merged code, tests, and documentation; planning alone does not close a ledger item.

Write only the feature's `tasks.md` and any necessary task references. Preserve IDs already used by contributors when revising the task list. Sync changed files to the KG if available, with Git files remaining the authority. Issue tracker publication is optional and requires user authorization.

This is step 5 of the planning flow in the spec-generator skill (constitution, specify, clarify, plan, tasks, analyze, implement). It reads the step 4 `plan.md`, whose sections follow `specs/_template/plan.md`, and writes only `tasks.md`. Every active requirement row needs a task line, and every task must name an existing row; the analyze step of `pipelines-hook spec-standard` fails a touched spec that breaks either rule. Phase the tasks the way the plan's Phase 2 task approach describes.
