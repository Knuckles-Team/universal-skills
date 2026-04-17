# Cinematic Frontend: Tailwind Construction

In a "1:1 Pixel Perfect" high-fidelity context, Tailwind CSS is used slightly differently than in standard dashboard construction. The focus is on macro-spacing, typography tracking, gradient math, and CSS filter effects to create depth, noise, and cinematic mood.

## 1. The Global Noise Overlay (Turbulence)
A defining characteristic of modern premium sites is a subtle noise overlay that prevents gradients and solid dark colors from banding on high-resolution displays. We define this globally, rather than repeating textures.

### Setup in `index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply antialiased selection:bg-accent/30 selection:text-white bg-background text-foreground;
  }
}

/* The Noise Layer */
.noise-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 50;
  opacity: 0.05; /* Adjust per preset: 0.03 for sleek, 0.08 for brutalist */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
```

Add `<div className="noise-overlay" />` to the root `App.jsx` layout.

## 2. Advanced Typography Scales & Tracking
Standard Tailwind typography uses default letter-spacing. Cinematic design requires extremely tight tracking on headings, high contrast in font families, and precise leading (`leading-tight` or `<line-height>`).

```javascript
// Excerpt of a Hero Typography block demonstrating contrast:
<div className="flex flex-col">
  <h1 className="text-6xl md:text-8xl tracking-tighter font-medium leading-[0.9] text-gray-200">
    Biology is the
  </h1>
  <h2 className="text-7xl md:text-9xl font-serif italic tracking-tight text-accent mt-2">
    Ultimate Hardware.
  </h2>
</div>
```

**Key utility adjustments:**
- Use `tracking-tighter` (-0.05em) on large sans-serif headings for a dense, architectural look.
- Use `leading-[0.9]` or `leading-none` for multi-line hero headers so lines sit very close together.
- Use monospace fonts (`font-mono`) with `tracking-widest` for small technical labels or "eyebrow" text.

## 3. High-End Button Design ("The Magnetic Button")
Standard Tailwind buttons look flat. Cinematic buttons require layered gradients, ring offsets, and smooth cubic-bezier transitions on hover.

```javascript
<button className="group relative overflow-hidden rounded-full px-8 py-4 font-medium
                   bg-zinc-900 border border-zinc-700/50 text-zinc-100 shadow-xl
                   transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl hover:border-zinc-500/50">

  {/* Shimmer background layer that slides in on hover */}
  <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-zinc-800/40 to-transparent
                  transition-transform duration-700 ease-[cubic-bezier(0.19,1,0.22,1)] group-hover:translate-x-full" />

  {/* Inner shadow/highlight ring to give 3D volume */}
  <div className="absolute inset-0 rounded-full ring-1 ring-inset ring-white/10" />

  {/* Button Text */}
  <span className="relative z-10 flex items-center gap-2">
    Execute Protocol
    <svg className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
    </svg>
  </span>
</button>
```

## 4. Complex Gradients and Background Blends
Never use solid `bg-black` behind a hero image. Use a heavy `bg-gradient-to-t` to create depth, melting the bottom of the image smoothly into the page background.

```javascript
<section className="relative h-[100dvh] w-full pt-32 pb-16 flex items-end">
  {/* Background Image Layer */}
  <div className="absolute inset-0 z-0">
    <img
      src="https://images.unsplash.com/photo-[your-image-id]"
      className="object-cover w-full h-full opacity-60 mix-blend-screen"
      alt="Atmosphere"
    />
  </div>

  {/* Gradient Overlay Layer - crucial for blending */}
  <div className="absolute inset-0 z-10 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A]/80 to-transparent" />

  {/* Vignette Overlay (darkens edges) */}
  <div className="absolute inset-0 z-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-black/20 to-black/80" />

  {/* Content Layer */}
  <div className="relative z-20 container mx-auto px-6">
     {/* Text content goes here */}
  </div>
</section>
```

## 5. Architectural Container Shapes
Rely heavily on extreme border radii (`rounded-[2rem]` or `rounded-[3rem]`) to soften the UI, moving away from sharp sharp CSS boxes toward "functional UI capsules."

```javascript
/* Standard feature card container */
<div className="relative overflow-hidden rounded-[2.5rem] bg-zinc-900 border border-zinc-800 p-10
                hover:border-zinc-700 transition-colors duration-500">
  {/* Subtle top inner glow */}
  <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

  {/* Content */}
</div>
```
