---
mode: append
---
## Steps

1. Start with `npx hyperframes reverse start <video> --dir <project>`. Verify that it prints the probe with size, fps and duration, or relay its refusal and upgrade link.
2. Find every cut with `npx hyperframes measure cuts <video>` and set the root size, `data-fps` and duration from the probe. Verify that each shot start in the project equals the listed frame divided by fps, rounded down.
3. Rebuild each layer in HTML, cut sub-assets from the original, and keep the original sound as one `<audio>`. Verify that `npx hyperframes diff <video> . --at <t,...>` shows no large cell difference at the sampled times.
4. Run `npx hyperframes check` and fix its errors, and render with `npx hyperframes cloud render --fps <data-fps> --quality high -o <out>`. Verify that `npx hyperframes diff <video> <out>` lists no missing cuts.
5. Fix what the diff names, render and diff once more, and write `REVERSE.md`. Verify that `ls REVERSE.md` exists and holds the last diff numbers.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `reverse start` refuses | Reverse is a Pro feature and the account is not on Pro | Give the person the printed upgrade link and its `fix` command to run themselves, then start again |
| A cut lands a frame late | The time was rounded to milliseconds | Write the time as frame divided by fps, rounded down, such as `2.766666` for frame 83 at 30 fps |
| The cloud render fails | The rate is fractional or the frame is not 16:9, 9:16 or 1:1 | Tell the person why and render locally with `npx hyperframes render -o <out>` in the foreground |
