# Contributing to the Graph OS ecosystem

The [contribution guide](https://github.com/Knuckles-Team/universal-skills/blob/main/CONTRIBUTING.md)
defines the shared specification workflow. Start with the target repository's
`AGENTS.md` and tracked `specs/` directory. Use GitHub Spec Kit for the feature
artifacts and the universal-skills `spec-generator`, `task-planner`, and
`spec-verifier` skills to author and review them. The `sdd-full-lifecycle` workflow
composes those skills.

Keep architecture, reusable component wiring, cross-repository contracts, test
scenarios, quality gates, and ledger IDs in the owning repository's spec. Link
related specs in other repositories. GitHub tracks the source files and review
history. At present, `docs/` is this repository's tracked MkDocs source and the
existing Pages workflow publishes it; [US-PAGES-001](https://github.com/Knuckles-Team/universal-skills/blob/main/specs/US-PAGES-001/spec.md)
tracks any later content consolidation. A published page
does not establish that a spec has been implemented: close a ledger item only after
merged code and acceptance evidence are verified.

Deployment instructions for a provider belong with that provider's source
documentation and published project site. The universal-skills checks validate
this repository's own skills and workflows; they do not require generated changes
to sibling provider READMEs.

Required cloud PR checks use deterministic fixtures or provision disposable
dependencies. Credentialed and live-environment checks run in a separately
reported scheduled or post-merge lane. Hermetic correctness and quality failures
remain required PR failures; see the contribution guide for the full policy.
