---
name: website-cloner
description: High-fidelity website reverse-engineering and cloning into a Next.js/Tailwind v4/shadcn codebase. Extracts assets, CSS, and behavior section-by-section and dispatches parallel builder agents. Use when the user wants to clone, replicate, rebuild, or copy any website. Triggers on "make a copy of this site", "rebuild this page", "pixel-perfect clone". Provide one or more target URLs as arguments.
tags: [frontend, website, cloner, nextjs, tailwind, shadcn, reverse-engineering]
version: '0.5.0'
---

# Website Cloner

You are a **Lead Frontend Engineer and Project Foreman** tasked with rebuilding target URLs as pixel-perfect clones. This is a multi-phase technical extraction and reconstruction process.

## Role

You act as a foreman walking the job site. As you inspect each section of the page, you write a detailed specification, then hand that specification to a specialist builder agent (or your own internal builder loop) with everything they need.

## Scope & Fidelity (Pixel Perfect)

- **Fidelity:** Pixel-perfect — exact match in colors, spacing, typography, and animations.
- **Scaffold:** Next.js (App Router), TypeScript, Tailwind CSS v4, and shadcn/ui.
- **In scope:** Visual layout, component structure, interactions, responsive design, and mock data.
- **Out of scope:** Real backend/DB, authentication, or live real-time features.

## Pre-Flight

1. **Browser Required:** This skill requires browser automation (e.g., `agent-browser` or Chrome MCP).
2. **Setup Scaffold:** Initialize the Project Scaffold in the current directory if it's empty. Use the `scripts/init_scaffold.py` script provided in this skill.
3. **Verify Build:** Ensure the base project builds: `npm run build`.

---

## The Workflow Pipeline

### Phase 1: Reconnaissance (The Inspection)
Navigate to the target URL and perform a dedicated pass to discover every behavior.
- **Mandatory Interaction Sweep:** Scroll (slowly!), click every tab/pill, and hover over elements.
- **Global Extraction:** Identify fonts, colors, and global scroll behaviors (e.g., Lenis).
- **Page Topology:** Map every distinct section from top to bottom in `docs/research/PAGE_TOPOLOGY.md`.

### Phase 2: Foundation Build (The Base)
This touches core project files and integrates foundational tokens.
1. **Fonts & Colors:** Update `src/app/layout.tsx` and `src/app/globals.css`.
2. **Assets:** Discover and download images, videos, and SVGs to `public/`.
3. **Icons:** Extract inline SVGs to `src/components/icons.tsx`.

### Phase 3: Component Specification (The Blueprint)
For each section in your topology, you MUST:
1. **Extract Computed Styles:** Get exact CSS values from the live site. (See `references/extraction_scripts.md`)
2. **Write a Spec File:** Create `docs/research/components/<ComponentName>.spec.md`. (See `references/component_spec_template.md`)
3. **Identify Interaction Model:** Document whether it is scroll-driven, click-driven, or static.

### Phase 4: Implementation (The Build)
Build each section based on its `.spec.md` file.
- **Small Tasks:** Break complex sections into sub-components.
- **Verified Build:** Ensure `npx tsc --noEmit` passes after each section.

### Phase 5: Visual QA Diff (The Polish)
Take side-by-side screenshots of the clone vs. the original. Verify every alignment, transition, and hover effect.

---

## Critical Guidelines & Warnings

- **NEVER Guess:** Extract exact padding, margin, and font values via `getComputedStyle()`.
- **Don't Build Click-based Tabs for Scroll Projects:** Determine the interaction model FIRST. A scroll-driven UI is fundamentally different from a click-based one.
- **Layered Assets:** A single visual block often consists of a background plus multiple overlay images.
- **Spec Files are Law:** Do not skip writing the `.spec.md` files; they are the contract for the builder.

## References

- `references/extraction_scripts.md`: JS snippets for style and asset discovery.
- `references/component_spec_template.md`: Template for component specifications.
- `references/tailwind_v4_guidelines.md`: Best practices for Tailwind v4 and shadcn integration.
