---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from the repository root. Verify that the JSON has absolute `FEATURE_DIR` and `AVAILABLE_DOCS` paths and that `tasks.md` exists.
2. Check `FEATURE_DIR/checklists/` for incomplete items with `grep -rc '^- \[ \]' <FEATURE_DIR>/checklists/`. Verify that every file reports 0, or ask the user before continuing.
3. Verify the ignore files for the detected stack, for example with `git check-ignore -v node_modules`. Verify that build output and dependency folders are ignored.
4. Execute the tasks phase by phase, honoring `[P]` parallel markers, and tick each finished task `[X]` in `tasks.md`. Verify that `grep -c '^- \[X\]' <FEATURE_DIR>/tasks.md` rises after each phase.
5. Run the repository gate `uvx pre-commit run --all-files` and the bound tests. Verify that the gate exits 0 and that every test is bound to its row with `spec: <ID>`.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The prerequisites script fails | `tasks.md` is missing | Run `speckit-tasks` first, then re-run the script |
| A checklist item is unchecked | A requirement gap is still open | Stop, ask the user whether to proceed, or fix the gap in the spec before coding |
| A task fails midway | A dependency or test is broken | Fix the cause, keep the task unticked, and re-run its test with the repository test command before continuing |
| The gate rejects the commit | The `Spec:` trailer is missing or a test is unbound | Add `Spec: <IDs>` directly above the `Co-Authored-By:` trailer and bind the test with `# spec: <ID>` |
