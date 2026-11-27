---
name: hyperframes-registry
domain: creative
skill_type: skill
license: Apache-2.0
description: About 450 ready-made HyperFrames blocks and components installed as editable source - transitions, overlays, titles, kinetic type, captions, charts, map overlays, 3D, camera moves. Use it before hand-building any named visual (CRT scanlines, glitch, film grain, a chart); also for hyperframes add and catalog.
metadata:
  version: '1.7.0'
---

**Plugin installs:** Inside a HyperFrames plugin, follow the rules in `references/plugin-installation.md` of the `hyperframes` skill.

**Telemetry:** this catalog omits the upstream usage beacon. Do not run any `hyperframes events` command, even if a reference file mentions one.

# HyperFrames registry

Starting from an item is faster and usually better than writing the effect yourself, and an installed item is ordinary source in your project: change it, cut it down, restyle it.

## Find and install

There is no `hyperframes registry` command; searching is `catalog`, installing is `add`.

```bash
npx hyperframes catalog --query "<what the beat should do, in English>" --json
npx hyperframes add <name> --json        # prints the written files and the mount snippet
```

- Query in English even when the video is not: the catalog is indexed in English, and another script returns `No searchable words in query`, which is not a gap.
- Search is local and sends nothing. The default `words` tier only finds items that reuse your words; `--on-device` ranks by meaning after a one-time ~33 MB download. Offer that download and let the person decide; never enable it silently. The `--json` envelope names the tier that answered.
- Narrow with `--type block|component` and `--tag <tag>`. `add <tag>` installs every block with that tag; dependencies install first. `add` needs the network even for an item installed before; search works offline from the cached manifest.
- Nothing fits: report it before you hand-build, on either tier. `catalog --query` prints the line pre-filled (`report_gap` in `--json`): `npx hyperframes feedback --search-miss "<query>" --wanted "<the move you needed>" --tier <tier>`. Describe the effect, not an item name you imagined.

Tiers, `dropped` and `unindexed`, stale indexes, offline behaviour: `references/search.md`.

## What's in it

| Blocks: a scene with its own timeline | Examples |
| --- | --- |
| Transitions | `beat-freeze-cut`, `chromatic-radial-split`, `cinematic-zoom` |
| Overlays and lower thirds | `camcorder-hud`, `editorial-flash-overlay`, `lt-clean-bar` |
| Title cards and kinetic type | `canopy-part-title`, `code-slice-hero` |
| Social, chat and UI cards | `ai-chat-reveal`, `chatgpt-exchange` |
| Code, charts, data and maps | `code-diff`, `bar-chart-race`, `data-chart` |
| 3D, shader and backgrounds | `app-showcase`, `aurora`, `blob` |

| Components: a snippet merged into your scene | Examples |
| --- | --- |
| Motion primitives and text effects | `agent-cursor`, `blur-in`, `bottom-up-letters` |
| Caption styles | `caption-clip-wipe`, `caption-editorial-emphasis` |
| Camera moves | `camera-shake`, `camera-scan-gate` |
| Product demo and UI props | `before-after-wipe`, `browser-device-stage` |
| Textures, particles and effects | `ascii-render-pass`, `grain-overlay` |

## Wiring

- **Block**: installs to `compositions/<name>.html`. Mount it with `data-composition-src`, `data-composition-id` matching the block's own id, `data-start` and the `data-duration` you need; the snippet `add` prints is the starting point. `references/wiring-blocks.md`.
- **Component**: installs to `compositions/components/<name>.html`. Copy its markup, `<style>` and script into your scene, and follow its comment block if it hooks into your timeline. `references/wiring-components.md`.
- Take the largest unit that fits, then edit it. Keep an installed item's ids prefixed as they are, so two items can't collide.
- An item keeps its own variables; set them for one mount with `data-variable-values` on its host (`add --vars '{"title":"…"}'` writes that), and point its colour and font variables at your brand's.
- Beat-synced blocks take hit times from `npx hyperframes beats --json`: the beat times minus the mount's `data-start`.
- Install paths come from `hyperframes.json` (`references/install-locations.md`).

## Contributing

Authoring a new block or component for an upstream PR: `references/contributing.md`, starter templates in `references/templates.md`, quality bar in `references/component-quality-bar.md`.

## Steps

1. Search the catalog with `npx hyperframes catalog --query "<what the beat should do, in English>" --json`. Verify that the envelope names the tier that answered and lists candidate items.
2. Install the chosen item with `npx hyperframes add <name> --json`. Verify that the output lists the written files and a mount snippet, and that `ls compositions/` shows the new file.
3. Mount a block with `data-composition-src` and a `data-composition-id` equal to its own id, or merge a component into your scene. Verify that `grep -n 'data-composition-id' index.html` shows the mount.
4. Set variables with `add --vars '{"title":"..."}'` or `data-variable-values` on the host. Verify that `npx hyperframes check --json` reports no errors for the mounted item.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| The catalog finds nothing | The query is not in English or the `words` tier lacks the term | Rephrase in English, or offer `--on-device` after telling the person about the ~33 MB download |
| `add` fails offline | `add` needs the network even for a cached item | Reconnect and re-run `npx hyperframes add <name> --json`, since search alone works offline |
| Two items collide | Their ids were renamed or unprefixed | Restore the prefixed ids the installed source shipped with |
| Nothing fits the effect | The registry has no matching item | Run the pre-filled `npx hyperframes feedback --search-miss` line from the catalog output, then hand-build |
