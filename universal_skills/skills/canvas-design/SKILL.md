---
name: canvas-design
domain: creative
skill_type: skill
description: >-
  Creates visual designs using HTML Canvas or SVG APIs for banners, social media
  assets, posters, or UI components. Use when the user requests programmatic
  graphic design, visual composition, or custom image generation without using a
  photo editor. Do NOT use for photo realistic image generation or general web UI
  layouts unless it specifically requires canvas/SVG.
license: MIT
tags: [canvas, svg, graphic-design, programmatic-design, composition]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# Canvas & SVG Design

Create professional-grade visual compositions programmatically using the HTML Canvas and SVG APIs.

---

## Technical Options

### 1. HTML Canvas (Raster-based)
Best for complex rendering, particle systems, pixel manipulation, and performance-heavy visual effects.

**Core Setup:**
```javascript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.width = 1200;
canvas.height = 630; // OG Image standard
```

**Common Patterns:**
- **Layers**: Draw multiple elements sequentially to create depth.
- **Gradients**: `ctx.createLinearGradient()` or `ctx.createRadialGradient()`.
- **Masking**: `ctx.globalCompositeOperation = 'source-atop'`.
- **Text**: `ctx.font = 'bold 48px Inter'`, `ctx.fillText()`.

### 2. SVG (Vector-based)
Best for sharp graphics, logos, icons, and illustrations that need to scale without quality loss.

**Core Setup:**
```javascript
const svg = `
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#1a1a1a" />
  <!-- elements go here -->
</svg>
`;
```

**Common Patterns:**
- **Paths**: `<path d="..." />` for complex shapes.
- **Groups**: `<g>` for organization and transformation nesting.
- **Filters**: `<defs><filter id="blur">...</filter></defs>` for effects.

---

## Design Principles for Programmatic Design

### 1. Grid & Layout
- Use mathematical ratios (Golden Ratio, Rule of Thirds).
- Define margins and gutters as percentage of width/height.
- Ensure visual balance across the frame.

### 2. Color Systems
- Define a base color palette (see `brand-guidelines`).
- Use HSL for easier mathematical manipulation (hue shifting, lightness variation).
- Implement programmatic contrast checking.

### 3. Typography
- Prioritize legibility.
- Define a clear hierarchy: Heading, Subheading, Meta, Body.
- Use programmatic spacing (kerning, line-height) consistent with the design scale.

---

## Workflow

### Step 1: Composition Planning
- Sketch the layout mathematically.
- Define the coordinate system (e.g., 0 to 100 on both axes).
- Identify key visual elements and their relationships.

### Step 2: Implementation
- Implement the background and foundational shapes.
- Add gradients, textures, or secondary patterns.
- Layer in typography and primary visual assets.
- Apply final effects (noise, blur, drop shadows).

### Step 3: Export
- Provide the self-contained HTML/JS or SVG code.
- Provide a preview command or a way to download the resulting PNG/SVG.

---

## Steps

1. Plan the composition by writing the canvas size and coordinate system, for example `grep -n "const w\|const h" design.js`. Verify that width, height and padding are defined once.
2. Implement the background and foundational shapes in `design.js` or an `.svg` file. Verify that `node --check design.js` reports no syntax errors for JavaScript output.
3. Layer in typography and final effects, checking font usage with `grep -n "font" design.js`. Verify that every text element uses a font and size defined in the design principles.
4. Export a self-contained HTML or SVG file and preview it, for example `agent-browser open file://$PWD/design.html`. Verify that the rendered output matches the planned layout.
5. Save a PNG with `agent-browser screenshot design.png`. Verify that `ls -l design.png` shows a non-empty file.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Text clipped or overlapping | Positions hard-coded instead of derived from width and height | Compute positions from `w`, `h` and `padding` as in the OG image example. |
| Blank canvas | Script runs before the canvas element exists or an exception occurred | Move the script after the canvas element and check the browser console for the error. |
| Font falls back to default | Font not loaded before drawing | Use a web-safe font or wait for `document.fonts.ready` before drawing text. |

## Example: OG Image Generator Template

```javascript
// Mathematical layout for an OG Image
const w = 1200;
const h = 630;
const padding = w * 0.05;

// Draw Background
ctx.fillStyle = '#111';
ctx.fillRect(0, 0, w, h);

// Draw Accent Gradient
const grad = ctx.createLinearGradient(0, 0, w, h);
grad.addColorStop(0, '#3b82f6');
grad.addColorStop(1, '#8b5cf6');
ctx.fillStyle = grad;
ctx.beginPath();
ctx.roundRect(padding, padding, w - padding*2, h - padding*2, 20);
ctx.fill();

// Draw Title
ctx.fillStyle = '#fff';
ctx.font = 'bold 80px Inter';
ctx.fillText('Programmatic Design', padding * 2, h/2);
```
