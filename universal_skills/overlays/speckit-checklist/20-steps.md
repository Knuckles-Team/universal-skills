---
mode: append
---
## Steps

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --template checklist-template` from the repository root. Verify that the JSON has `FEATURE_DIR`, `AVAILABLE_DOCS` and `TEMPLATE_CONTENT`.
2. Ask up to three contextual questions about scope, depth and audience, and combine the answers with `$ARGUMENTS`. Verify that the stated checklist domain is one short phrase.
3. Read `spec.md`, `plan.md` and `tasks.md` as needed from `FEATURE_DIR`. Verify that each item you plan to write cites a spec section or a gap marker.
4. Write the checklist under `FEATURE_DIR/checklists/` as requirement-quality tests, using the template structure. Verify that `ls <FEATURE_DIR>/checklists/` lists the new file.
5. Report the file path, the item count and whether the file was created or appended. Verify that the count equals `grep -c '^- \[ \]' <file>`.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The script fails with a missing spec | No feature spec exists yet | Run `speckit-specify` first, then re-run the script |
| Items test the code instead of the requirements | The checklist was written as a test plan | Rewrite each item as a question about requirement clarity, completeness or measurability |
| An unchecked item blocks the gate | The requirement gap is real | Fix the spec for that item, then tick it, and name the fix in the item note |
