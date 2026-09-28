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
  version: '1.3.2'
  author: Genius
---

# Spec Verifier

Verify one feature directory at repository root: `specs/<stable-id>/`. Read `spec.md`, `plan.md`, `tasks.md`, applicable design artifacts and `checklists/`, plus `.specify/memory/constitution.md`. Use the live repository and relevant related repositories as evidence. The tracked spec files are authoritative; graph-os is a derived index to query for concept drift when available.

Evaluate every user story and functional requirement against acceptance criteria, design decisions, executable tasks, and a test scenario. Check that `plan.md` names existing components and wiring to reuse, interfaces, data flows, migration and failure handling, architecture boundaries, and cross-repository contracts. Verify that tasks cover integration into a real execution path and the affected documentation. Resolve public requirement IDs and related public spec paths; mark absent or stale links as failures, not completed work. Reject a spec that requires a private draft, plan repository, internal GitLab host, homelab inventory, or local workspace path to understand or complete it. Check that every cross-repository ID has one normative owner and that consumer links do not claim a second owner.

Check the constitution and the repository's configured CCCC, `jscpd`, and Dupehound thresholds, plus KISS, for unjustified duplication or complexity. Report unavailable tools or undefined thresholds as gaps; never fabricate green results. Check actual test evidence, including negative and integration cases. Keep specification quality checks distinct from implementation test results.

Write a concise `specs/<stable-id>/DRIFT_REPORT.md` with requirement-to-task-to-test coverage, missing design or contracts, ambiguities, terminology drift, quality gate results, public ID and cross-repository link status, and evidence links. Write `specs/<stable-id>/checklists/requirements.md` as a binary specification-quality checklist, using Spec Kit's checklist layout. Each failed item names a specific fix. End the report with **Pass**, **Fail**, or **Needs revision** and a coverage fraction. Never mark a requirement landed solely because these documents exist; verify `status.json` delivery and acceptance against exact public revision, test, and consumer or release receipts. Report KG lookup or sync failures separately from the file-based verdict.
