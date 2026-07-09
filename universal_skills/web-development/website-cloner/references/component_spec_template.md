# Component Specification Template

Use this template to create a detailed blueprint for each component or section BEFORE dispatching a builder agent. Save to `docs/research/components/<ComponentName>.spec.md`.

---

# <ComponentName> Specification

## Overview
- **Target file:** `src/components/<ComponentName>.tsx`
- **Screenshot:** `docs/design-references/<screenshot-name>.png`
- **Interaction model:** <static | click-driven | scroll-driven | time-driven>

## DOM Structure
<Describe the element hierarchy — what contains what. E.g., "Outer div with relative positioning containing a sticky nav and a scrollable content area.">

## Computed Styles (exact values from getComputedStyle)

### Container
- display: ...
- padding: ...
- maxWidth: ...
- (List every property from extraction result that isn't default)

### <Child element 1>
- fontSize: ...
- fontWeight: ...
- color: ...
- (List every relevant property)

### <Child element N>
...

## States & Behaviors

### <Behavior Name, e.g., "Scroll-triggered Floating Mode">
- **Trigger:** <Exact mechanism — e.g., "scroll position > 50px", "IntersectionObserver rootMargin: -30% 0px">
- **State A (Before):** maxWidth: 100vw, boxShadow: none, borderRadius: 0
- **State B (After):** maxWidth: 1200px, boxShadow: 0 4px 20px rgba(0,0,0,0.1), borderRadius: 16px
- **Transition:** transition: all 0.3s ease
- **Implementation Approach:** <CSS transition + scroll listener | Framer Motion | CSS animation-timeline | etc.>

### Hover States
- **<Element Name>:** <Property>: <Before Value> → <After Value>, transition: <Value>

## Per-State Content (if applicable)

### State: "<State Name>"
- Title: "..."
- Subtitle: "..."
- Cards Data: [...]

## Assets
- Background image: `public/images/<file>.webp`
- Overlay image: `public/images/<file>.png`
- Icons used: `<SearchIcon>`, `<ArrowRightIcon>` from `src/components/icons.tsx`

## Text Content (verbatim)
<Copy-paste all text content exactly as it appears on the live site>

## Responsive Behavior

- **Desktop (1440px):** <Layout description>
- **Tablet (768px):** <What changes — e.g., "sidebar collapses into menu">
- **Mobile (390px):** <What changes — e.g., "stacks to single column, images reduced to 80%">
- **Breakpoint:** Layout switches at approximately <N>px
