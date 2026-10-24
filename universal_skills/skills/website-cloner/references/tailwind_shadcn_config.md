# Tailwind v4 & shadcn/ui Configuration

These snippets represent the standardized configuration for the high-fidelity Next.js clones.

## 1. Tailwind v4 (`globals.css`)
Tailwind CSS v4 moves most configuration into the CSS file itself using the `@theme` block.

```css
@import "tailwindcss";

@theme {
  /* Color Palette (Extracted from target) */
  --color-background: oklch(0.98 0 0); /* Example: Pearl */
  --color-foreground: oklch(0.12 0 0); /* Example: Charcoal */

  --color-primary: oklch(0.55 0.18 200); /* Example: Slate Blue */
  --color-primary-foreground: oklch(1 0 0);

  --color-accent: oklch(0.64 0.22 25); /* Example: Terra Cotta */

  --color-muted: oklch(0.92 0.02 0);
  --color-muted-foreground: oklch(0.45 0.04 0);

  /* Border Radii (Extracted from target) */
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-3xl: 2rem;

  /* Typography (Extracted from target) */
  --font-heading: "Inter", sans-serif;
  --font-body: "Outfit", sans-serif;

  /* Keyframe Animations */
  @keyframes fade-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
}

/* Layer Utilities */
@layer utilities {
  .noise-overlay {
    position: relative;
    &::after {
      content: "";
      position: absolute;
      inset: 0;
      opacity: 0.05;
      pointer-events: none;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    }
  }
}
```

## 2. Global Layout (`src/app/layout.tsx`)
Standardized font loading and SEO metadata.

```tsx
import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "Target Website Clone",
  description: "High-fidelity reconstruction using AI.",
  icons: {
    icon: "/seo/favicon.ico",
    apple: "/seo/apple-touch-icon.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body className="antialiased selection:bg-primary/20">{children}</body>
    </html>
  );
}
```

## 3. Custom Icons (`src/components/icons.tsx`)
Wrap extracted SVGs in standard React components.

```tsx
import { cn } from "@/lib/utils";

export const ArrowRightIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("w-5 h-5", className)}
  >
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
);
```

## 4. shadcn/ui Utility (`src/lib/utils.ts`)
The standard `cn` helper for class merging.

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```
