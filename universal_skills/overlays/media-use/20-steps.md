---
mode: append
---
## Steps

1. Run `npx hyperframes auth status` whenever the request needs a HeyGen model or the catalog. Verify that it shows a signed-in account, or ask the person to run `npx hyperframes auth login` themselves.
2. List reusable assets with `npx hyperframes media-use resolve --type <type> --intent "<what you need>" --project <dir> --candidates`. Verify that you judged each candidate's fit before making anything new.
3. Resolve the asset with `npx hyperframes media-use resolve --type <type> --intent "<what you need>" --project <dir>`. Verify that it prints one `resolved <id> -> <path>` line and that `ls <dir>/assets/` shows the file.
4. For footage looks, apply one intent with `npx hyperframes media-treatment`, never CSS filters. Verify that `npx hyperframes check --json` passes after the change.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The call is refused for a missing sign-in | The person is not logged in | Tell them in one line that sign-in is free and ask them to run `npx hyperframes auth login` in the prompt |
| A paid call is refused over the limit | The credit limit in `.hyperframes/credit-limit.json` would be exceeded | Say what does not fit, ask before dropping it, and run the `billing` command the refusal names only after the person does |
| `heygen` is not found | The HeyGen CLI is not installed | Give the install link from `references/heygen.md` and wait until the person says it is installed |
