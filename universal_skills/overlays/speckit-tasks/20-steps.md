---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/setup-tasks.sh --json` from the repository root. Verify that the JSON names `FEATURE_DIR`, `TASKS_TEMPLATE_CONTENT` and `AVAILABLE_DOCS`.
2. Read `plan.md`, `spec.md` and the optional design documents listed in `AVAILABLE_DOCS`. Verify that every user story in `spec.md` has a priority you can cite.
3. Write `tasks.md` from the template, one phase per story, each task as `- [ ] T001 [P] [US1] <ROW-ID> description`. Verify that `grep -c '^- \[ \] T[0-9]' <FEATURE_DIR>/tasks.md` equals the planned task count.
4. Check row coverage: every active row has a task line and every task names an existing row. Verify that `pipelines-hook spec-standard` reports no row without a task and no task without a row.
5. Report the task count, the story breakdown and the MVP scope. Verify that the counts match the `grep -c` result above.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `setup-tasks.sh` is absent | `.specify/scripts/` is missing | Derive `FEATURE_DIR` from the repository root and the stable ID, and read `.specify/templates/tasks-template.md` directly |
| A task has no requirement row ID | The task was written from the plan alone | Add the owning `<ROW-ID>` from `spec.md`, or delete the task if no row owns it |
| A task has no file path | The description was left abstract | Name the exact file the task edits, as in `src/<path>`, and mark `[P]` only when files differ |
