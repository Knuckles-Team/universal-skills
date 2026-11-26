---
mode: append
---
## Steps

1. Write each slide as a top-level scene with `data-composition-id`, `data-start`, `data-duration` and `data-label`. Verify that `grep -c 'data-composition-id' <file>` equals the slide count.
2. Add one `application/hyperframes-slideshow+json` island near the top of `<body>`, in the HTML. Verify that `grep -n 'hyperframes-slideshow+json' <file>` shows exactly one island.
3. Run `npx hyperframes check --json` until it is clean. Verify that every `sceneId` resolves, every hotspot `target` exists and fragments sit inside their slide.
4. Take stills with `npx hyperframes snapshot --at <t,...>` for each slide, never a render. Verify that the PNGs exist under `.hyperframes/artifacts/snapshots/`.
5. Serve the deck with `npx hyperframes present <project-dir>`. Verify that the printed URL answers 200 and hand it to the person.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `check` reports an unresolved `sceneId` | The id does not match a scene's `data-composition-id` | Correct the id in the island or add `startTime` and `endTime` |
| A fragment is rejected | It is an offset inside the slide, not an absolute time | Use absolute timeline times within the slide's start and end |
| An MP4 render shows one scene | `render` keeps only the first scene of a deck | Use `snapshot --at` for stills and `present` for the deck |
| Clicks do nothing on a slide | A hidden stacked slide swallows them | Set `opacity: 0`, `visibility: hidden` and `pointer-events: none` together on hidden slides |
