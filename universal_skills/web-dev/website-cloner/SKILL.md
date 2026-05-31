---
name: website-cloner
description: >-
  High-fidelity website reverse-engineering and cloning into a Next.js/Tailwind
  v4/shadcn codebase. Extracts assets, CSS, and behavior section-by-section and
  dispatches parallel builder agents. Use when the user wants to clone, replicate,
  rebuild, or copy any website. Triggers on "make a copy of this site", "rebuild
  this page", "pixel-perfect clone". Provide one or more target URLs as arguments.
license: MIT
tags: [frontend, website, cloner, nextjs, tailwind, shadcn, reverse-engineering]
metadata:
  author: Genius
  version: '0.35.2'
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

## Workflow

### Step 1: browser-setup

Set up the browser environment and project structure:
- **Browser Required:** Ensure browser automation is available (e.g., `agent-browser` or Chrome MCP).
- **Setup Scaffold:** Initialize the Project Scaffold in the current directory if it is empty using `scripts/init_scaffold.py`.
- **Verify Build:** Ensure the base project compiles successfully via `npm run build`.

### Step 2: reconnaissance [depends_on: browser-setup]

Navigate to the target URL and perform a comprehensive visual audit:
- **Mandatory Interaction Sweep:** Scroll (slowly!), click every tab/pill, and hover over elements to discover dynamic behaviors.
- **Global Extraction:** Identify custom web fonts, core colors, and global scroll libraries (e.g., Lenis).

### Step 3: page-topology [depends_on: reconnaissance]

Map out the layout page structure:
- **Page Topology:** Map every distinct visual section from top to bottom in `docs/research/PAGE_TOPOLOGY.md`.

### Step 4: fonts-colors [depends_on: page-topology]

Build the CSS and token framework for the clone:
- **Fonts & Colors:** Update `src/app/layout.tsx` and `src/app/globals.css` with extracted variables.
- **Global Layout:** Configure base margins, overflow, and custom typography classes.

### Step 5: asset-extraction [depends_on: page-topology]

Gather standard media assets:
- **Assets:** Discover and download images, videos, and standard assets to `public/`.

### Step 6: icon-extraction [depends_on: page-topology]

Gather vector icon assets:
- **Icons:** Extract inline SVGs directly to `src/components/icons.tsx` as reusable components.

### Step 7: component-spec [depends_on: fonts-colors, asset-extraction, icon-extraction]

Map precise styles and interactions for every section identified in the topology:
- **Extract Computed Styles:** Gather exact CSS values from the live site via `getComputedStyle()` (see `references/extraction_scripts.md`).
- **Write a Spec File:** Create a detailed blueprint at `docs/research/components/<ComponentName>.spec.md` (see `references/component_spec_template.md`).
- **Identify Interaction Model:** Document whether each component is scroll-driven, click-driven, or static.

### Step 8: component-build [depends_on: component-spec]

Implement the page sections in code:
- **Small Tasks:** Break down complex sections into modular, sub-components.
- **Verified Build:** Ensure typing and builds pass via `npx tsc --noEmit` after implementing each section.

### Step 9: visual-diff-qa [depends_on: component-build]

Verify that the rebuilt site is pixel-perfect:
- **Side-by-Side Screenshots:** Capture screenshots of the clone and the target website to verify every spacing element, hover transition, and font weight matches perfectly.

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
