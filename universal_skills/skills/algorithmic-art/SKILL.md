---
name: algorithmic-art
description: Creates generative algorithmic art using p5.js with seeded randomness and interactive HTML artifacts. Use when the user requests generative art, algorithmic art, computational aesthetics, flow fields, particle systems, or creative coding. Output is self-contained interactive HTML. Do NOT use for UI design, data visualization charts, or photo editing.
categories: [Creative]
tags: [generative-art, p5js, creative-coding, algorithmic, canvas, interactive]
---

# Algorithmic Art Creation

Create gallery-quality generative algorithmic art: define a computational philosophy, implement it in p5.js with seeded randomness, and output a self-contained interactive HTML artifact.

---

## Step 1: Define an Algorithmic Philosophy (write as `.md` file)

Before any code, articulate the **computational philosophy** — the generative aesthetic movement that will guide the implementation.

**The philosophy must express (4–6 paragraphs):**
- The computational process and mathematical relationships
- The role of randomness, noise, and emergence
- Particle behaviors, field dynamics, or system states
- Temporal evolution and parameter variation
- Emphasis on craftsmanship: the algorithm should feel meticulously refined

**Philosophy format:**

```
Name: [1-2 word movement name, e.g. "Organic Turbulence"]

[4-6 paragraphs describing:
- The conceptual core
- How it manifests algorithmically
- Seeded variation and emergent complexity
- The feeling of computational craftsmanship]
```

**Examples:**
- "Organic Turbulence": Flow fields from layered Perlin noise. Particles follow vector forces, trails accumulate into organic density maps. Color emerges from velocity — fast particles burn bright, slow ones fade to shadow.
- "Stochastic Crystallization": Random circle packing evolving through relaxation. Cells push to equilibrium. The organic tiling feels both random and inevitable.

**Anti-patterns:** Do not create static images, basic shapes, or templates. Everything must emerge through algorithmic process.

---

## Step 2: Implement in p5.js

### Technical Requirements

**Seeded Randomness (always):**
```javascript
let seed = 12345;
randomSeed(seed);
noiseSeed(seed);
```

**Parameter Structure:**
```javascript
let params = {
  seed: 12345,
  // Add parameters specific to this algorithm:
  // quantities, scales, speeds, probabilities, ratios, thresholds
};
```

**Canvas:**
```javascript
function setup() {
  createCanvas(1200, 1200);
  // Initialize system
}
function draw() {
  // Algorithm — can be static (noLoop) or animated
}
```

### Craftsmanship Requirements

- **Balance**: Complexity without visual noise; order without rigidity
- **Color**: Thoughtful palettes — not random RGB values
- **Composition**: Visual hierarchy and flow even within randomness
- **Performance**: Smooth execution, optimized for real-time if animated
- **Reproducibility**: Same seed MUST always produce identical output

---

## Step 3: Create Interactive HTML Artifact

Build a **single self-contained HTML file** with everything inline. No external files except the p5.js CDN.

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
  <style>
    /* Clean minimal layout */
    body { display: flex; margin: 0; font-family: sans-serif; background: #1a1a1a; }
    #canvas-container { flex: 1; }
    #controls { width: 260px; padding: 20px; background: #2a2a2a; color: #eee; }
  </style>
</head>
<body>
  <div id="canvas-container"></div>
  <div id="controls">
    <!-- Seed section (always include) -->
    <section>
      <label>Seed: <span id="seed-display">12345</span></label>
      <button onclick="prevSeed()">←</button>
      <button onclick="nextSeed()">→</button>
      <button onclick="randomSeed()">Random</button>
    </section>
    <!-- Parameters section (customize per artwork) -->
    <section>
      <div class="control-group">
        <label>Particle Count</label>
        <input type="range" min="100" max="5000" value="1000"
               oninput="updateParam('count', this.value)">
        <span id="count-value">1000</span>
      </div>
      <!-- Add controls for each parameter -->
    </section>
    <!-- Actions section (always include) -->
    <section>
      <button onclick="regenerate()">Regenerate</button>
      <button onclick="resetParams()">Reset</button>
      <button onclick="downloadPNG()">Download PNG</button>
    </section>
  </div>
  <script>
    // All p5.js code, parameter objects, classes, seed controls inline here
  </script>
</body>
</html>
```

**Required interactive features:**
- Seed display + Previous / Next / Random / Jump-to-seed controls
- Sliders for each numeric parameter with live update
- Regenerate and Reset buttons
- Download PNG button

---

## Output

Deliver:
1. **Algorithmic Philosophy** — as a markdown file (Step 1)
2. **Interactive HTML Artifact** — single self-contained file (Step 3)
