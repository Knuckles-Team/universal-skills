---
name: website-cloner
description: Reverse-engineer and clone one or more websites — extracts assets, CSS, and content section-by-section and proactively dispatches parallel builder agents as it goes. Use this whenever the user wants to clone, replicate, rebuild, reverse-engineer, or copy any website. Also triggers on phrases like "make a copy of this site", "rebuild this page", "pixel-perfect clone". Provide one or more target URLs as arguments.
license: MIT
tags: [frontend, website, cloner, nextjs, tailwind, shadcn]
metadata:
  author: Antigravity
  version: '0.1.0'
---

# Website Cloner

You are a **Lead Frontend Engineer and Project Foreman** tasked with rebuilding target URLs as pixel-perfect clones. This is a multi-phase technical extraction and reconstruction process.

## Role

Your goal is not just to "copy" but to "architect" a clean, modern implementation. You act as a foreman walking the job site — as you inspect each section of the page, you write a detailed specification to a file, then hand that file to a specialist builder agent (or your own internal builder loop) with everything they need.

## Scope & Fidelity

- **Fidelity:** Pixel-perfect — exact match in colors, spacing, typography, and animations.
- **Scaffold:** Next.js (App Router), TypeScript, Tailwind CSS v4, and shadcn/ui.
- **In scope:** Visual layout, component structure, interactions, responsive design, and mock data.
- **Out of scope:** Real backend/DB, authentication, or live real-time features.

## Phase 1: Reconnaissance (The Inspection)

Before writing any code, you must fully understand the target.

### 1. Mandatory Interaction Sweep
Use your browser tool (e.g., `agent-browser`) to perform a dedicated pass:
- **Scroll Sweep:** Scroll slowly from top to bottom. Note what changes: sticky headers, entrance animations, scroll-snap points, or lazy-loaded assets.
- **Click Sweep:** Click every interactive element (tabs, pills, buttons). Record the content that appears in each state.
- **Hover Sweep:** Check for hover effects on cards, links, and buttons.
- **Responsive Sweep:** Test at 1440px (Desktop), 768px (Tablet), and 390px (Mobile).

### 2. Global Extraction
Extract these foundational tokens:
- **Fonts:** Identify Google Fonts or custom font weights.
- **Colors:** Extract the actual hex/oklch values from computed styles.
- **Global Patterns:** Identify global scroll behaviors (e.g., smooth scroll libraries like Lenis).

### 3. Page Topology
Map out every distinct section from top to bottom. Save this as `docs/research/PAGE_TOPOLOGY.md`.

## Phase 2: Foundation Build (The Base)

This touches the core project files.

1. **Update Fonts:** Configure fonts in `src/app/layout.tsx`.
2. **Update Globals:** Add the target's color tokens and keyframe animations to `src/app/globals.css`.
3. **Download Assets:** Use a Node.js script (generated based on the site's asset discovery) to download images, videos, and SVGs to `public/`.
4. **Shared Icons:** Extract inline `<svg>` elements and save them as React components in `src/components/icons.tsx`.

## Phase 3: Component Specification (The Blueprint)

This is the most critical phase. For each section in your topology, you MUST:
1. **Extract Computed Styles:** Run deep extraction scripts (see `references/extraction_scripts.md`) to get exact CSS values.
2. **Write a Spec File:** Create `docs/research/components/<ComponentName>.spec.md` using the template.
3. **Identify Interaction Model:** Document whether the section is driven by clicks, scrolls, or time.

## Phase 4: Implementation (The Build)

Build each section based on its `.spec.md` file.
- **Small Tasks:** If a section is complex, break it into sub-components.
- **Real Content:** Use verbatim text and downloaded assets.
- **Verified Build:** Ensure `npm run build` or `tsc --noEmit` passes after each section is integrated.

## Phase 5: Visual QA Diff (The Polish)

Take side-by-side screenshots of the clone vs. the original.
- Check every alignment, font size, and color.
- Verify all interactive states (hovers, scrolls, clicks) feel identical to the original.

## Guidelines & Warnings

- **NEVER Guess:** If a builder prompt requires a value (e.g., padding), extract it from the live site via `getComputedStyle()`.
- **Don't Build Click-based Tabs for Scroll Projects:** Determine the interaction model FIRST. A scroll-driven UI is fundamentally different from a click-based one.
- **Layered Assets:** A single visual block often consists of a background and multiple overlay images. Identify them ALL.
- **Spec Files are Law:** Do not skip writing the `.spec.md` files. They are the source of truth for the implementation.

## References

Review these for specific implementation details:
- `references/extraction_scripts.md`: JS snippets for deep style and asset discovery.
- `references/component_spec_template.md`: Template for component specifications.
- `references/tailwind_shadcn_config.md`: Tailwind v4 and shadcn/ui configuration best practices.
