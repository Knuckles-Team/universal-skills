# UI/UX Heuristic Evaluation Reference

Standards and evaluation criteria for automated UI/UX grading.

## Nielsen's 10 Usability Heuristics (Adapted for Static Analysis)

### H1: Visibility of System Status
**Web**: Loading indicators, progress bars, spinners, skeleton screens.
**TUI**: Status bars, spinners, progress indicators, real-time feedback.

### H2: Match Between System and Real World
**Web**: Semantic HTML (`<nav>`, `<main>`, `<article>`), natural labels, familiar icons.
**TUI**: Natural command names, descriptive help text, familiar terminology.

### H3: User Control and Freedom
**Web**: Navigation, undo/redo, back buttons, cancel actions, clear exit paths.
**TUI**: Ctrl+C handling, exit/quit commands, confirmation prompts, `--dry-run` flags.

### H4: Consistency and Standards
**Web**: CSS variables/design tokens, component reuse, consistent naming.
**TUI**: Consistent color scheme, key binding conventions, uniform output formatting.

### H5: Error Prevention
**Web**: Form validation, required fields, confirmation dialogs, type constraints.
**TUI**: Input validation, `--dry-run` flags, confirmation prompts, safe defaults.

### H6: Recognition Rather Than Recall
**Web**: Visible navigation, breadcrumbs, labeled buttons, dropdown menus, tooltips.
**TUI**: Tab completion, command suggestions, autocomplete, discoverability.

### H7: Flexibility and Efficiency of Use
**Web**: Responsive design, keyboard navigation, shortcuts, customizable layouts.
**TUI**: Keyboard shortcuts, config files, aliases, power-user commands.

### H8: Aesthetic and Minimalist Design
**Web**: Clean layout, appropriate whitespace, color system, visual hierarchy.
**TUI**: Aligned output, box drawing, tables, color coding, readable formatting.

### H9: Help Users Recognize, Diagnose, and Recover from Errors
**Web**: Error boundary components, descriptive error messages, toast notifications.
**TUI**: Descriptive stderr, meaningful exit codes, formatted exception output.

### H10: Help and Documentation
**Web**: Tooltips, help pages, documentation links, onboarding guides.
**TUI**: `--help` flag, man pages, usage examples, README quick-start.

---

## WCAG 2.1 AA Key Criteria (Web Only)

| Check | Requirement |
|-------|-------------|
| Alt tags | All `<img>` elements have descriptive `alt` attributes |
| ARIA labels | Interactive elements have `aria-label` or `aria-labelledby` |
| Role attributes | Custom widgets use appropriate `role` attributes |
| Language | `<html>` element has `lang` attribute |
| Focus management | Tab order is logical, focus traps are handled |
| Color contrast | Sufficient contrast ratios, `prefers-color-scheme` support |

---

## System Usability Scale (SUS) Reference

The SUS is a standardized 10-item questionnaire yielding a score from 0–100. Key benchmarks:

| Score | Percentile | Interpretation |
|-------|-----------|----------------|
| 80.3+ | Top 10% | Excellent usability |
| 68 | Average | Industry baseline |
| 51 | Bottom 25% | Poor usability |
| <50 | Bottom 15% | Unacceptable |

> **Note**: SUS requires human evaluation. The code-enhancer skill uses static heuristic analysis as a proxy. For full SUS scoring, integrate user testing feedback.

---

## TUI-Specific Quality Indicators

| Indicator | Evidence Pattern |
|-----------|-----------------|
| Color accessibility | Supports `NO_COLOR` env var, theme system |
| Keyboard-first design | All actions accessible via keyboard |
| Output alignment | Tables, columns, consistent indentation |
| Error formatting | Rich tracebacks, colored error levels |
| Help coverage | Every command has `--help`, every option has description |
| Responsive layout | Adapts to terminal width (`shutil.get_terminal_size`) |
