---
name: theme-factory
description: Creates design themes and token systems for applications, websites, and UI components. Use when the user requests a new visual theme, dark/light mode variants, color scheme expansion, or design token definitions. Do NOT use for general branding or individual component styling.
categories: [Creative, Design]
tags: [theming, design-tokens, design-system, css-variables, color-schemes, dark-mode]
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
