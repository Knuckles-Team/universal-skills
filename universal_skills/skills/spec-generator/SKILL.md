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
  version: '1.6.0'
  author: Genius
---

# SDD Spec Generator

Produce the **intent specification** for one stable feature ID. Use GitHub Spec Kit's resolved `spec-template` and `specs/<stable-id>/spec.md` convention. The repository root is the path base. Keep `.specify/` for Spec Kit project configuration, templates, and `.specify/memory/constitution.md`; do not place feature artifacts beneath `.specify/` or `agent_data/`.

## Planning flow

Run the steps in order. Each step names the files it writes and the gate that checks them (`pipelines-hook spec-standard` unless stated). Keep row IDs, `Spec:` trailers and test bindings throughout; the state is computed, never written.

| Step | Writes | Gate |
|---|---|---|
| 1. Constitution | `.specify/memory/constitution.md` from the pipelines `specs/_template/constitution.md` | Constitution check (advisory until present) |
| 2. Specify | `spec.md` (stories, `FR-`/`SC-` labels, Edge Cases, Assumptions) and the `requirements.md` rows | Narrative, title, ID and file-set checks |
| 3. Clarify | Resolves each `[NEEDS CLARIFICATION: ...]` marker in `spec.md` and `requirements.md` | Clarification check fails while one remains |
| 4. Plan | `plan.md` from `specs/_template/plan.md`: Summary, Technical Context, Constitution Check, Project Structure, Phase 0 to 2, Complexity Tracking, Build contract, Production caller chain, Cross-repo seams. Also `research.md`, `data-model.md`, `contracts/` and `quickstart.md` where the plan calls for them | Plan check (sections and Technical Context fields) |
| 5. Tasks | `tasks.md`, one `- [ ] T001 [P] [US1] <ID>-R012.4 description` line per row (use the task-planner skill) | Task-line check |
| 6. Analyze | Fixes the gaps the analysis reports: a row with no task or no test, a task naming no row, an orphan `FR-`/`SC-` label, an open marker in any design file; fills `checklists/requirements.md` from `specs/_template/checklists/requirements.md` (use the spec-verifier skill) | Consistency analysis and checklist check (fail for a touched spec) |
| 7. Implement | Code and bound tests (`# spec: <ID>`), commits with a `Spec:` trailer | `pipelines-hook spec-status` computes `LANDED` and `VERIFIED` |

## Inputs and authority

Read the feature request, existing repository code and docs, relevant `specs/`, the repository constitution, and any source ledger or draft plan entry. Treat drafts as private input to distill, never as a dependency of the published spec. Query arbora code context, search, and concept tools when available to find existing components and concept IDs. Files in the owning public repository are the reviewable source of truth; KG records are a derived index. If arbora is unavailable, continue from repository evidence and record the missing lookup as an open question. Do not invent ledger completion or claim a component exists without evidence.

Use a stable, human-readable ID that survives branch changes. Keep the same ID in the feature directory, document heading, public requirement register, and related repositories. Link exact public requirement IDs, public issue/PR evidence, and related public `specs/<id>/` documents by repository and path. Never link or name private draft repositories, plan paths, internal GitLab hosts, homelab inventory, or a contributor's local workspace. Copy every necessary design, interface, acceptance criterion, and test condition into owner-native specs so a contributor with only public GitHub access can implement and verify the deliverable. If the feature crosses repositories, name the one normative owner of each behavior and the public contract connecting its consumers; each owning repository keeps its own complete local spec.

Start from the repository constitution at `.specify/memory/constitution.md`. If it is absent, create it from the pipelines `specs/_template/constitution.md`: one page that links the organization standards by public URL. Check the draft against the constitution before you write the plan.

Resolve only ambiguities that block a testable requirement. If the user has not answered, write the marker `[NEEDS CLARIFICATION: <question>]` in `spec.md` and state the effect on implementation. Do not silently choose a behavior. The landing gate refuses a spec that still holds a marker, so resolve and delete each marker before the row lands.

## Required `spec.md` content

- Purpose and scope, actors, and prioritized user stories (`### User Story N - <title> (Priority: P1)`) with Given/When/Then acceptance scenarios. Add the sections Edge Cases and Assumptions, and explicit out-of-scope items. Number the functional requirements `FR-001` and the measurable success criteria `SC-001`. Each `FR-` and `SC-` label must name the `-R` requirement rows in `requirements.md` that it maps to.
- Stable traceability table: public requirement ID, owning repository, related public spec ID, and evidence needed for acceptance. A source ledger row can remain open or partial until verified; creating a spec never marks it landed. Do not expose private source paths or require a draft to interpret the requirement.
- Existing wiring and reuse: entry points, current implementation and contracts to extend, dependency and downstream impact, and any genuine gap. Require a new component to connect to a real execution path.
- Architecture and design obligations for `plan.md` (a Technical Context block and a Constitution Check against `.specify/memory/constitution.md`), `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`, where applicable. Name relevant interfaces, data flows, migration/compatibility constraints, failure modes, observability, and security boundaries. Keep implementation choices in design artifacts rather than writing speculative code details into user-facing requirements.
- Test specification: map each acceptance criterion and functional requirement to a unit, integration, contract, end-to-end, or manual verification scenario, including negative cases, fixtures, expected result, and evidence location. Record justified test omissions.
- Quality requirements: identify the repository's configured CCCC, `jscpd`, and Dupehound commands/thresholds and require their applicable gates; apply KISS by reusing existing wiring and avoiding unnecessary abstractions. If a tool or threshold is absent, specify the gap and decision needed instead of inventing a passing score.

Do not demand unrelated documentation edits by default. Name the README, AGENTS.md, changelog, architecture docs, and code docs actually affected by the feature, with a testable reason for each.

## Output

Write the tracked `specs/<stable-id>/spec.md` and its `requirements.md` rows. Never write `status.json` or a `Status:` line: the generator computes the state from rows, `Spec:` trailers and test bindings. Use the resolved Spec Kit template when available and preserve its required sections. Put any specification-quality checklist in `specs/<stable-id>/checklists/`, following Spec Kit conventions. A complete spec awaiting implementation is `SPECIFIED`. It becomes `LANDED` when a commit with its `Spec:` trailer reaches the default branch, and `VERIFIED` when a bound test exists. Sync changed files to the KG when the ingestion tool is available, but treat a failed KG sync as a reported indexing failure rather than a reason to overwrite Git artifacts. Optional issue tracker publication requires user authorization.
