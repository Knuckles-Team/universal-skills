---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/setup-plan.sh --json` from the repository root. Verify that the JSON names `FEATURE_SPEC`, `IMPL_PLAN`, `FEATURE_DIR` and `BRANCH`.
2. Read `FEATURE_SPEC` and `.specify/memory/constitution.md`, and fill Technical Context and the Constitution Check in `IMPL_PLAN`. Verify that `grep -n 'NEEDS CLARIFICATION' <IMPL_PLAN>` lists only unknowns you will resolve in Phase 0.
3. Phase 0: resolve each unknown in `research.md` with Decision, Rationale and Alternatives. Verify that `grep -c 'Decision' research.md` equals the number of unknowns.
4. Phase 1: write `data-model.md`, `contracts/` and `quickstart.md` where the plan calls for them. Verify that `ls <FEATURE_DIR>` shows each artifact the plan names.
5. Re-check the Constitution Check after the design and report the branch, plan path and artifacts. Verify that every gate in `IMPL_PLAN` is marked pass or justified under Complexity Tracking.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `setup-plan.sh` fails or is absent | `.specify/scripts/` is missing or no feature directory exists | Run `speckit-specify` to create `specs/<stable-id>/`, or copy `.specify/templates/plan-template.md` to `specs/<stable-id>/plan.md` by hand |
| The Constitution Check fails | A design choice conflicts with a repository principle | Change the design to comply, or record the violation and its justification under Complexity Tracking |
| Unresolved `NEEDS CLARIFICATION` remain after Phase 0 | A research task was skipped | Add the missing research item to `research.md` and answer it, or send it back through `speckit-clarify` |
