---
mode: append
---
## Steps

1. Resolve the active template with `.specify/scripts/bash/resolve-template.sh constitution-template --json` from the repository root. Verify that the JSON carries a non-empty `TEMPLATE_CONTENT`.
2. Draft the constitution from that template: one page that links the organization standards by public URL and adds only repository-specific principles. Verify that no bracketed placeholder token remains by running `grep -n '\[[A-Z_]*\]' .specify/memory/constitution.md`, which should print nothing.
3. Write the result to `.specify/memory/constitution.md` with a Sync Impact Report HTML comment at the top. Verify that `head -n 5 .specify/memory/constitution.md` shows the comment.
4. Run `pipelines-hook spec-standard` against the repository. Verify that its constitution check passes and report any other finding to the user.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `resolve-template.sh` is missing or exits non-zero | `.specify/scripts/` is absent or the template name is wrong | Read `.specify/templates/constitution-template.md` directly and confirm the file exists with `ls .specify/templates/` |
| Placeholders remain after drafting | A value was not derived from the repository or the user input | Re-run `grep -n '\[[A-Z_]*\]' .specify/memory/constitution.md`, fill each hit from repo facts, and mark genuinely unknown values `TODO(<FIELD>)` with a reason |
| `pipelines-hook spec-standard` fails the constitution check | The file is not at `.specify/memory/constitution.md` | Move the file to that exact path and confirm with `ls .specify/memory/constitution.md` |
