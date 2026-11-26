---
mode: append
---
## Steps

1. Write the composition and run `npx hyperframes lint` after the first pass. Verify that it exits 0 or lists errors you can fix by file and line.
2. Run `npx hyperframes check --json` and fix every error. Verify that the output shows nonzero samples, since `0 samples` means nothing was checked.
3. Run `npx hyperframes snapshot` and read the PNGs. Verify that `ls .hyperframes/artifacts/snapshots/` lists one image per scene midpoint.
4. Start `npx hyperframes preview --background` and hand the person the URL. Verify that the URL answers 200 before you share it.
5. On approval, run `npx hyperframes render --quality looks -o out.mp4`. Verify that `ffprobe -v error -show_entries format=duration out.mp4` matches the root `data-duration`.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Chrome is missing or will not start | The browser was never installed | Run `npx hyperframes browser ensure`, and gate on `.ok` from `npx hyperframes doctor --json` |
| A timeline edit is refused | The clip would overlap a neighbour or end past its composition | Use `--overwrite`, move the neighbour first, or raise the root `data-duration` |
| `capture` writes `BLOCKED.md` | The site refused the capture | Take nothing from the partial files and re-run `capture` into a new `-o` folder |
| The disk is tight | Old renders and caches piled up | Run `npx hyperframes clean --dry-run` and then `clean`, and never delete `.hyperframes` |
