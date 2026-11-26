---
name: theme-factory
domain: web-development
skill_type: skill
description: >-
  Creates design themes and token systems for applications, websites, and UI
  components. Use when the user requests a new visual theme, dark/light mode
  variants, color scheme expansion, or design token definitions. Do NOT use for
  general branding or individual component styling.
license: MIT
tags: [theming, design-tokens, design-system, css-variables, color-schemes, dark-mode]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# Theme Factory

Generate comprehensive, accessible, and scalable design themes using a tokens-first approach.

---

## The Tokens-First Approach

Themes should be defined using **Design Tokens** (CSS variables) rather than hardcoded values. This ensures consistency and enables instant theme switching (e.g., light to dark).

### 1. Primitive Tokens (The RAW values)
The base colors, spacing, and typography without semantic meaning.
```css
:root {
  --blue-500: #3b82f6;
  --gray-900: #111827;
  --spacing-4: 1rem;
}
```

### 2. Semantic Tokens (The PURPOSE)
Values mapped to a specific role in the UI.
```css
[data-theme="light"] {
  --bg-primary: #ffffff;
  --text-main: var(--gray-900);
  --accent: var(--blue-500);
}

[data-theme="dark"] {
  --bg-primary: var(--gray-900);
  --text-main: #f9fafb;
  --accent: var(--blue-400);
}
```

---

## Theme Components

### 1. Color Palette Expansion
For any primary brand color, generate a functional scale (50–900).
- **50–200**: Light backgrounds, subtle borders.
- **400–600**: Primary actions, main brand presence.
- **700–900**: Dark text, deep contrast elements.

### 2. Elevating Surfaces (Z-Index and Shadows)
Define how elements "lift" off the background.
- **Level 0**: Background / Base.
- **Level 1**: Cards, sections.
- **Level 2**: Modals, popovers, tooltips.

### 3. Typography & Spacing
- Scale should be modular (e.g., 1.25 ratio).
- Spacing should be based on a fixed unit (e.g., 4px or 8px grid).

---

## Steps

1. Identify the base brand color and vibe from the request and the existing project. Verify with `grep -rn "\-\-accent\|--primary" --include=*.css .` whether tokens already exist, and extend them rather than replace.
2. Define the primitive tokens (color scales 50 to 900, spacing, type scale) in a `:root` block. Verify with `grep -c -- "--" theme.css` that the file lists the expected scale steps.
3. Map semantic tokens for `[data-theme="light"]` and `[data-theme="dark"]`. Verify with `grep -n "data-theme" theme.css` that both variants exist.
4. Check contrast for each text-on-background pair, aiming for at least 4.5:1 for body text. Verify the ratios with a contrast calculator or `python3 -c` using the WCAG luminance formula, and record any failures.
5. Provide the implementation (CSS, `tailwind.config.js` or theme object) with a usage snippet. Verify that the snippet references only semantic tokens such as `var(--accent)`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Dark mode text fails contrast | Dark tokens reuse light-mode values | Pick a lighter step (for example `--gray-50`) for `--text-main` and recompute the ratio |
| Components ignore the theme | They use hardcoded values instead of tokens | Replace literals with semantic `var(--...)` references |
| Token sprawl | A token was created for every property | Remove tokens that do not cover a recurring role and keep the core set |
| Tailwind classes do not pick up tokens | Config does not extend the theme | Add the variables to `theme.extend.colors` in `tailwind.config.js` |

## Design Systems Supported

- **Vanilla CSS**: CSS Custom Properties (`--variable`).
- **Tailwind CSS**: `tailwind.config.js` extensions.
- **Styled Components**: Theme provider objects.
- **Figma Variables**: Structured JSON export.

---

## Interaction Workflow

### Step 1: Definition
Identify the base "brand vibe" or existing brand color.
- Is it high-energy (vibrant), professional (muted), minimal, or experimental?
- Identify the core primary color.

### Step 2: Generation
Generate the token set:
- **Core palette** (Functional scales for Primary, Secondary, Grey, Semantic).
- **Surface system** (Backgrounds, Borders, Cards).
- **Interactive states** (Hover, Active, Focus, Disabled).
- **Dark Mode** variant (Ensuring WCAG contrast compliance).

### Step 3: Implementation Guide
Provide the CSS or configuration file and show how to apply it:
```html
<button class="bg-[var(--accent)] text-[var(--text-on-accent)]">
  Click Me
</button>
```

---

## Best Practices

- **Accessibility First**: Always verify contrast of `text-on-background` for every level of the theme.
- **Naming Consistency**: Use consistent naming like `bg-base`, `bg-subtle`, `text-muted`, `text-strong`.
- **Avoid Over-Theming**: Don't create tokens for every single property; focus on the core system that covers 90% of use cases.
