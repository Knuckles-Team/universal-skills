# Tailwind CSS v4 Guidelines

The `website-cloner` scaffold uses Tailwind CSS v4, which introduces significant changes in how design tokens and configuration are handled.

## Key Differences from v3

1.  **CSS-First Configuration**: Instead of `tailwind.config.js`, variables are ideally defined directly in `src/app/globals.css` using the `@theme` block.
2.  **OKLCH Colors**: Use `oklch` for colors to ensure precision and modern color space support.
3.  **No Config File (Optional)**: Most projects no longer need `tailwind.config.js` as the `@theme` block in CSS handles everything.

## How to Implement Design Tokens

When you extract colors and fonts from a target site, update `src/app/globals.css`:

```css
@import "tailwindcss";

@theme {
  /* Colors */
  --color-primary: oklch(0.6 0.2 260);
  --color-secondary: oklch(0.7 0.1 200);

  /* Fonts */
  --font-sans: "Inter", ui-sans-serif, system-ui;

  /* Animations */
  --animate-fade-in: fade-in 0.5s ease-out;

  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}
```

## Mapping to shadcn/ui

The scaffold integrates shadcn/ui with Tailwind v4. When updating the theme, ensure you map the target's colors to the expected shadcn variable names for consistent component styling:

- `--background` / `--foreground`
- `--primary` / `--primary-foreground`
- `--muted` / `--muted-foreground`
- `--accent` / `--accent-foreground`

## Best Practices for Cloning

- **Exact Values**: Use the `oklch()` values extracted from the site if possible.
- **Dynamic Variable Usage**: Use `@apply` in CSS or standard Tailwind classes in JSX.
- **Verification**: Always run `npm run build` to ensure the Tailwind compiler correctly picks up your `@theme` overrides.
