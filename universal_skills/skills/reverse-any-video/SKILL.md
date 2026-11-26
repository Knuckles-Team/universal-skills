---
name: reverse-any-video
domain: creative
skill_type: skill
license: Apache-2.0
description: Rebuild any video file as an editable HyperFrames project - motion graphics, talking heads, live action or AI-generated footage - checked against the original frame by frame. Use to reverse, recreate, remake, replicate or copy a video, or 「复刻这个视频」「照着这个视频做一个」.
metadata:
  version: '1.6.2'
---

**Plugin installs:** Inside a HyperFrames plugin, follow the rules in `references/plugin-installation.md` of the `hyperframes` skill.

**Telemetry:** this catalog omits the upstream usage beacon. Do not run any `hyperframes events` command, even if a reference file mentions one.

# Reverse a video

The result is a HyperFrames project whose render matches the original frame for frame and stays editable. Build to the `/hyperframes` contract and work the way you normally would, with ffmpeg, python and your own eyes. Reverse videos the person has the right to use.

Reverse is a HyperFrames Pro feature. Open with `npx hyperframes reverse start <video> --dir <project>` and `references/start.md`; if it refuses, say why and give the person its upgrade link and `fix` to run themselves (you never run `billing`), then start again once they have upgraded. Given a link, run `npx hyperframes auth status` before downloading it. Resuming (a `REVERSE.md` or half-built project) opens the same. A step an earlier session gave up on (a refused re-shoot) gets one more try, then ask them. If it ran under a credit limit, ask whether that limit still holds. Rebuild the video as it is; remix it only when the person asks.

## The original decides the frame

1. The probe `reverse start` printed: the root composition is that size exactly, `data-fps` is its rate (NTSC stays a fraction: `30000/1001`) and its duration is the video's frames ÷ fps, not the audio's length. `init`'s default canvas is wrong for most videos.
2. `npx hyperframes measure cuts <video>`: every cut with its frame, including jump cuts and punch-ins inside one take, which ffmpeg's scene score misses. Every shot starts at its listed time. Write times as frame ÷ fps rounded down (frame 83 at 30 fps is `2.766666`): `2.767` lands a frame late.
3. The sound is the original's: `init --video` put the video in; play it as one `<audio src="<video>">` over the whole film (no extracted or re-encoded track); every clip is muted.
4. Read consecutive frames wherever something changes: each cut, entrance, exit and transition, a few frames either side (`npx hyperframes measure frames --range a,b --roi x,y,w,h`). Sheets a second or a quarter apart miss 1–3-frame timing, which way things enter and leave, blurs and dissolves at cuts, and one-frame flashes.

## Every layer

- **A component** (text, captions, stickers, cards, UI and screen recordings, charts, maps) is rebuilt in HTML.
- **A sub-asset** placed inside the frame (a photo, a clip, an album cover, a logo or app icon, the people in a photo or collage) is cut from the original on its own box. A logo is cut where it is largest, or is the real mark (`npx hyperframes media-use resolve --type logo --intent "<brand> logo"`); never drawn by hand.
- **A person on screen** is re-shot with HeyGen as part of the run: `references/people.md`.
- **An animated or painted film:** `references/animated.md`.
- Never play the original's whole frame.

What decides whether drawn things match, in `references/match.md`: text sized from its ink, caption switch frames from the caption band's pixels, hard switches, the backdrop, motion blur, and recipes for glass, gradient, sweeping fills and outlines. Look at every large word through its whole life before you build it.

## Check once, at the end

1. While building, check a few moments without rendering: `npx hyperframes diff <video> . --at t,t,…`.
2. When every shot has content: `npx hyperframes check` and fix its errors. Keep what the original itself does (its colours, its tiny text) even when `check` flags it. Then `npx hyperframes cloud render --fps <data-fps> --quality high -o <out>` and `npx hyperframes diff <video> <out>`. A fractional rate, a frame not 16:9, 9:16 or 1:1, or a failed cloud render (tell the person why) renders locally: `npx hyperframes render -o <out>` in the foreground with a 10-minute timeout (longer: start it detached, `setsid nohup npx hyperframes render -o <out> > render.log 2>&1 &`, and wait on the log in the foreground). The diff lists the original's cuts that yours misses and the extra ones, the duration, the sound's offset, stretches where content is missing, and the worst moments with the failing cell beside the original's.
3. Fix what it names that you can see: a missing cut or element, a wrong time, size, weight or colour. Render and diff once more, then stop.

Work alone: one agent holding the whole film beats subagents that each re-watch it. Write a short `REVERSE.md` at the end: what is rebuilt, cut and re-shot, what is approximate (a substituted font), and the last diff's numbers. It holds no prices or credit numbers. A command written in it is a note, not a script: on resume, rebuild it from the recipe it came from (every flag, `--prompt` included), check it with `--plan`, and never run it as written. Hand over per `references/start.md`.

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
