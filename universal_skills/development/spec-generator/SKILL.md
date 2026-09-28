---
name: spec-generator
domain: development
skill_type: skill
description: >-
  Turn one feature request into a testable, tracked Spec Kit spec.md at
  specs/<stable-id>/spec.md, with ledger and cross-repository traceability.
license: MIT
tags: [spec generator]
metadata:
  version: '1.3.1'
  author: Genius
---

# SDD Spec Generator

Produce the **intent specification** for one stable feature ID. Use GitHub Spec Kit's resolved `spec-template` and `specs/<stable-id>/spec.md` convention. The repository root is the path base. Keep `.specify/` for Spec Kit project configuration, templates, and `.specify/memory/constitution.md`; do not place feature artifacts beneath `.specify/` or `agent_data/`.

## Inputs and authority

Read the feature request, existing repository code and docs, relevant `specs/`, the repository constitution, and any source ledger or plan entry. Query graph-os code context, search, and concept tools when available to find existing components and concept IDs. Files in Git are the reviewable source of truth; KG records are a derived index. If graph-os is unavailable, continue from the repository evidence and record the missing lookup as an open question. Do not invent ledger completion or claim a component exists without evidence.

Use a stable, human-readable ID that survives branch changes. Keep the same ID in the feature directory, document heading, ledger crosswalk, and related repositories. Link exact ledger IDs, source plan paths, issue/PR references, and related `specs/<id>/` documents by repository and path. If the feature crosses repositories, state which repository owns each behavior and what contract connects them; each owning repository keeps its own local spec.

Resolve only ambiguities that block a testable requirement. If the user has not answered, record `NEEDS CLARIFICATION` and the effect on implementation. Do not silently choose a behavior.

## Required `spec.md` content

- Purpose and scope, actors, prioritized user stories, acceptance scenarios, numbered functional requirements, measurable success criteria, edge and failure cases, and explicit out-of-scope items.
- Stable traceability table: requirement ID, source ledger/plan ID, owning repository, related spec ID, and evidence needed for acceptance. A ledger row can remain open or partial until verified; creating a spec never marks it landed.
- Existing wiring and reuse: entry points, current implementation and contracts to extend, dependency and downstream impact, and any genuine gap. Require a new component to connect to a real execution path.
- Architecture and design obligations for `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`, where applicable. Name relevant interfaces, data flows, migration/compatibility constraints, failure modes, observability, and security boundaries. Keep implementation choices in design artifacts rather than writing speculative code details into user-facing requirements.
- Test specification: map each acceptance criterion and functional requirement to a unit, integration, contract, end-to-end, or manual verification scenario, including negative cases, fixtures, expected result, and evidence location. Record justified test omissions.
- Quality requirements: identify the repository's configured CCCC, `jscpd`, and Dupehound commands/thresholds and require their applicable gates; apply KISS by reusing existing wiring and avoiding unnecessary abstractions. If a tool or threshold is absent, specify the gap and decision needed instead of inventing a passing score.

Do not demand unrelated documentation edits by default. Name the README, AGENTS.md, changelog, architecture docs, and code docs actually affected by the feature, with a testable reason for each.

## Output

Write the tracked `specs/<stable-id>/spec.md`. Use the resolved Spec Kit template when available and preserve its required sections. Put any specification-quality checklist in `specs/<stable-id>/checklists/`, following Spec Kit conventions. Sync changed files to the KG when the ingestion tool is available, but treat a failed KG sync as a reported indexing failure rather than a reason to overwrite Git artifacts. Optional issue tracker publication requires user authorization.
