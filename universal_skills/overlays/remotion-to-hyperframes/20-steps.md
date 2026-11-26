---
mode: append
---
## Steps

1. For Remotion, run `python3 <SKILL_DIR>/scripts/lint_source.py <source dir>`. Verify that it reports no blockers, or host or refactor each blocker out as `references/escape-hatch.md` says.
2. Translate to the `/hyperframes` contract with one sub-composition per scene and times as `frame / fps`. Verify that `grep -c 'data-start' index.html` is at least the scene count.
3. Score frames with `npx hyperframes diff <original.mp4> . --at <t,...>` and on the full render with `npx hyperframes diff <original.mp4> <hf.mp4>`. Verify that SSIM meets the tier in `references/eval.md`.
4. Write what did not translate cleanly to `TRANSLATION_NOTES.md`. Verify that `ls TRANSLATION_NOTES.md` exists and names each dropped or approximated item.
5. In the final message list each imported part with its level (`Native`, `Hosted` or `Media`). Verify that every part from the source appears in the list.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `lint_source.py` reports blockers | Source uses `useState`, `useEffect` with dependencies or a React UI kit | Host the code or refactor the blocker out, and never approximate it |
| Every bordered element is too large | The Remotion `box-sizing` rule is missing | Add `* { box-sizing: border-box; }` once to the root `index.html` `<style>` |
| The diff is off by about 0.05 SSIM | The Remotion side was rendered with different encoder settings | Render it with `Config.setVideoImageFormat("png")` and `Config.setColorSpace("bt709")` and diff again |
| Code depends on wall-clock time or the network | It cannot be driven by timeline time | Render it to a file and bring it in at the Media level |
