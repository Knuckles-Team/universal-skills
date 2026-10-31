---
name: spec-verifier
domain: development
skill_type: skill
description: >-
  Verify one tracked specs/<stable-id>/ feature against its constitution, design,
  tasks, tests, quality gates, ledger links, and cross-repository contracts.
license: MIT
tags: [verifier, sdd, qa]
metadata:
  version: '1.5.2'
  author: Genius
---

# Spec Verifier

Verify one feature directory at repository root: `specs/<stable-id>/`. Read `spec.md`, `plan.md`, `tasks.md`, applicable design artifacts and `checklists/`, plus `.specify/memory/constitution.md`. Use the live repository and relevant related repositories as evidence. The tracked spec files are authoritative; arbora is a derived index to query for concept drift when available.

Evaluate every user story and functional requirement against acceptance criteria, design decisions, executable tasks, and a test scenario. Check that `plan.md` names existing components and wiring to reuse, interfaces, data flows, migration and failure handling, architecture boundaries, and cross-repository contracts. Verify that tasks cover integration into a real execution path and the affected documentation. Resolve public requirement IDs and related public spec paths; mark absent or stale links as failures, not completed work. Reject a spec that requires a private draft, plan repository, internal GitLab host, homelab inventory, or local workspace path to understand or complete it. Check that every cross-repository ID has one normative owner and that consumer links do not claim a second owner.

Check the constitution (a missing `.specify/memory/constitution.md` is a gap), fail any open `[NEEDS CLARIFICATION: ...]` marker, fail a written `Status:` line or tracked `status.json`, and check the repository's configured CCCC, `jscpd`, and Dupehound thresholds, plus KISS, for unjustified duplication or complexity. Report unavailable tools or undefined thresholds as gaps; never fabricate green results. Check actual test evidence, including negative and integration cases. Keep specification quality checks distinct from implementation test results.

Write a concise `specs/<stable-id>/checklists/analysis.md` (lower case; plain bullets, no unchecked task boxes) with requirement-to-task-to-test coverage, missing design or contracts, ambiguities, terminology drift, quality gate results, public ID and cross-repository link status, and evidence links. Write `specs/<stable-id>/checklists/requirements.md` as a binary specification-quality checklist, starting from `.specify/templates/checklist-template.md`; an unchecked item fails the gate for a touched spec. Each failed item names a specific fix. End the report with **Pass**, **Fail**, or **Needs revision** and a coverage fraction. Never mark a requirement landed solely because these documents exist; read the computed state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) with `pipelines-hook spec-status`; it comes from `Spec:` trailers and test bindings, not from a file. Report KG lookup or sync failures separately from the file-based verdict.

This is step 6 (analyze) of the planning flow in the spec-generator skill. Run `pipelines-hook spec-standard` first and treat its consistency findings as the baseline: a row with no task line, a task naming no row, a behaviour row with neither a bound test nor a test-spec entry, an orphan `FR-` or `SC-` label, and an open clarification marker in any design file. Check the optional artifacts too: a `contracts/` document per cross-repo seam (wire shape, refusal codes, owner row IDs on both sides, human-written), `data-model.md` for new types, ontology classes or tables, `quickstart.md` for a `served` behaviour row, `research.md` only when Phase 0 lists unknowns, and `checklists/requirements.md`. Check lower-case kebab-case names and the one place of plans, templates and the constitution. Check also that `plan.md` holds the template sections with a Constitution Check that passes or justifies each failure under Complexity Tracking.
