---
mode: append
---
## Steps

1. Start a new project with `npx hyperframes init <dir> --skip-skills --skill=hyperframes`, or read an existing one with `npx hyperframes timeline --json`. Verify that `ls <dir>` shows `index.html` and `compositions/`.
2. Write scenes as sub-compositions under the Contract rules, with a paused timeline registered per `window.__timelines`. Verify that every timed element has `class="clip"`, `data-start` and `data-duration` by running `grep -c 'class="clip"' index.html`.
3. Run `npx hyperframes check --json` after your last edit. Verify that it reports no errors and that you have weighed every warning.
4. For a film, run `npx hyperframes snapshot --review` and write `REVIEW.md` per `references/review.md`. Verify that the snapshot PNGs exist under `.hyperframes/artifacts/snapshots/`.
5. Open the Studio preview with `npx hyperframes preview --background` and wait for approval before rendering. Verify that the printed project URL answers HTTP 200.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `check --json` reports a rule violation | A clip lacks timing attributes or tweens `display` | Apply the `Fix:` line it prints, then re-run `npx hyperframes check --json` until it is clean |
| Fonts render in the wrong family | The family is not a bundled font | Add `@font-face` to a file under `assets/fonts/`, as `references/format.md` describes |
| The render length is wrong | The root `data-duration` does not match the plan | Set the root `data-duration` in seconds and re-run `check` |
