# Agent Skill Quality Rubric (CE-026)

Quality grading rubric for agent skills, ported from the
[skill-check](https://github.com/thedaviddias/skill-check) project and
adapted for the code-enhancer analysis pipeline.

## Scoring Model

Five weighted categories — each starts at its weight value and is reduced by
rule violations.  Errors deduct 1× the category weight, warnings deduct 0.5×.

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Frontmatter | 30% | Required fields (name, description), naming conventions, field order |
| Description | 30% | Length adequacy, "Use when" phrasing, anti-trigger phrases |
| Body | 20% | Line/token limits, section structure (`##` headings) |
| Links | 10% | Local markdown reference resolution |
| File/Meta | 10% | Trailing newlines, duplicate names/descriptions across skills |

## N/A Handling

If no `SKILL.md` files are discovered in the repository, the domain is scored
as **N/A** and excluded from the overall GPA calculation.

## Rule Reference

### Frontmatter Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `skill.frontmatter.required` | error | SKILL.md must have valid YAML frontmatter |
| `skill.frontmatter.name_required` | error | Frontmatter must include `name` |
| `skill.frontmatter.description_required` | error | Frontmatter must include `description` |
| `skill.frontmatter.name_matches_directory` | error | Name must match the parent directory slug |
| `skill.frontmatter.name_slug_format` | error | Name must be lowercase-kebab-case |
| `skill.frontmatter.name_max_length` | error | Name must not exceed 64 characters |
| `skill.frontmatter.field_order` | warn | `name` should precede `description` |
| `skill.frontmatter.unknown_fields` | warn | Only spec-defined fields allowed |

### Description Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `skill.description.non_empty` | error | Description must not be empty |
| `skill.description.max_length` | error | Max 1024 characters |
| `skill.description.use_when_phrase` | warn | Should contain "Use when" phrasing |
| `skill.description.min_recommended_length` | warn | Recommended minimum 50 characters |
| `skill.description.anti_trigger` | warn | Should contain "Do NOT use" anti-trigger |

### Body Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `skill.body.max_lines` | error | Max 500 lines |
| `skill.body.max_tokens` | warn | Recommended max ~5000 tokens |
| `skill.body.has_sections` | warn | Should have ≥2 `##` section headings |

### Link Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `skill.links.local_resolves` | warn | Local markdown links must resolve |
| `skill.links.references_resolve` | warn | Referenced files must exist |

### File/Meta Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `skill.file.trailing_newline` | warn | Single trailing newline required |
| `skill.duplicates.name` | warn | Skill names must be unique across the set |
| `skill.duplicates.description` | warn | Skill descriptions must be unique |

## Discovery Patterns

Skills are discovered via these glob patterns, excluding `.venv/` and
`node_modules/`:

```
**/skills/*/SKILL.md
**/SKILL.md
**/.claude/skills/*/SKILL.md
**/.cursor/skills/*/SKILL.md
**/.gemini/skills/*/SKILL.md
```

## Attribution

This rubric is adapted from the [skill-check](https://github.com/thedaviddias/skill-check)
project by David Dias (MIT License).  The scoring model and rule semantics are
ported to Python for self-contained execution within the code-enhancer skill.
