---
mode: append
---
## Steps

1. Generate a 2-4 word short name and the feature directory `specs/<stable-id>` (or the user's `SPECIFY_FEATURE_DIRECTORY`). Verify that `ls specs/` lists the directory with no duplicate prefix.
2. Resolve the template with `.specify/scripts/bash/resolve-template.sh spec-template --json` and write `TEMPLATE_CONTENT` to `specs/<stable-id>/spec.md`. Verify that `head -n 5 specs/<stable-id>/spec.md` shows the template title.
3. Fill the spec from the feature description, keeping section order, with at most 3 `[NEEDS CLARIFICATION]` markers. Verify that `grep -c 'NEEDS CLARIFICATION' specs/<stable-id>/spec.md` prints 3 or less.
4. Validate the spec against the quality checklist in `specs/<stable-id>/checklists/requirements.md`. Verify that every item is checked or that each failing item names a concrete fix.
5. Report the feature directory, the spec file path and the checklist results to the user. Verify that the report names the path printed by `ls specs/<stable-id>/spec.md`.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The template resolver fails | `.specify/scripts/` is absent or a preset layer is broken | Derive the directory from the repository root and the stable ID, and copy the section list from `.specify/templates/spec-template.md` |
| More than 3 clarification markers remain | Gaps were left open instead of guessed | Replace each low-impact marker with a reasonable default recorded under Assumptions, and keep only scope, security and user-experience questions |
| The spec names frameworks or databases | Implementation detail leaked into success criteria | Rewrite each hit as a measurable, technology-agnostic outcome and re-check with the quality checklist |
