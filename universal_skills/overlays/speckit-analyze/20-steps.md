---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks` once from the repository root. Verify that the JSON has `FEATURE_DIR` and that `spec.md`, `plan.md` and `tasks.md` all exist.
2. Run `pipelines-hook spec-standard` and keep its findings as the baseline. Verify that you can list each finding with its row ID.
3. Load only the needed parts of the spec, plan and tasks, and run the detection passes (passes A to F in the skill) for duplication, ambiguity, gaps, constitution conflicts and inconsistency, reading with `sed -n`. Verify that every finding cites a file and line or row ID.
4. Write `specs/<stable-id>/checklists/analysis.md` with the coverage table, ending in Pass, Fail or Needs revision plus a coverage fraction. Verify that `tail -n 3 specs/<stable-id>/checklists/analysis.md` shows the verdict.
5. Offer remediation for the top issues without editing any file. Verify that `ls specs/<stable-id>/` shows only the new `checklists/analysis.md` as changed.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The prerequisites script fails with a missing file | `tasks.md` or `spec.md` was not generated yet | Run `speckit-tasks` or `speckit-specify` first, then repeat the check |
| Findings flood the report | Low-severity items were listed in full | Cap the table at 50 rows, sort by severity and summarize the overflow |
| A tool or threshold is unavailable | `pipelines-hook` is not installed | Report it as a gap in `analysis.md`, never as a pass |
