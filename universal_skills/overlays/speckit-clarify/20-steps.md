---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` once from the repository root. Verify that the JSON has `FEATURE_DIR` and `FEATURE_SPEC` and that `ls` shows the spec file.
2. Scan `FEATURE_SPEC` with the ambiguity taxonomy and queue at most 5 questions, asking them one at a time. Verify that each question is answerable by a short choice or a phrase of 5 words or fewer.
3. After each accepted answer, write it into the matching section of `FEATURE_SPEC` under a `Clarifications` heading. Verify that `grep -n 'Clarifications' <FEATURE_SPEC>` shows the new entry.
4. Re-validate `FEATURE_DIR/checklists/requirements.md` if it exists. Verify that no contradictory statement remains and that `grep -c 'NEEDS CLARIFICATION' <FEATURE_SPEC>` printed after the run is lower than before it.
5. Report the questions answered, the sections touched and the coverage summary. Verify that the report lists every section heading listed by `grep -n '^## ' <FEATURE_SPEC>` that you edited.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The prerequisites script returns no JSON | The feature branch or directory is not set up | Run `speckit-specify` first, or pass the feature directory explicitly and re-run the script |
| An answer contradicts an earlier spec statement | The old statement was kept next to the new one | Replace the earlier text instead of appending, then re-run the checklist validation |
| The landing gate still finds a `[NEEDS CLARIFICATION: ...]` marker | A marker was left in `spec.md` or `requirements.md` | Resolve it, delete the marker, and confirm with `grep -rn 'NEEDS CLARIFICATION' specs/<stable-id>/` |
