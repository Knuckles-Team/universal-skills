---
name: marp-presentations
domain: docs
skill_type: skill
description: >-
  Create professional Marp presentation slides using Markdown. Use when the user
  requests slide creation, presentations, pitch decks, lecture materials, or Marp
  documents. Triggers include "create slides", "make a presentation", "Marp
  document", or requests to "make it look good" for slides. Do NOT use for web-
  based interactive presentations — use web-artifacts instead.
license: MIT
tags: [marp, presentations, slides, markdown, design]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# Marp Presentation Creator

Create professional, visually appealing presentations using [Marp](https://marp.app/) — a Markdown-to-slides framework. Every Marp file is a plain `.md` file rendered into beautiful slides.

---

## Theme Selection

Choose the appropriate theme based on content type:

| Content Type | Recommended Theme |
|-------------|-------------------|
| Technical/Developer | `tech` or `dark` |
| Business/Corporate | `business` |
| Academic/Minimal | `minimal` |
| Creative/Events | `colorful` or `gradient` |
| General/Unknown | `default` |

---

## Steps

1. Understand the requirements (content, audience, formality) and select a theme from the table above, such as `theme: tech` for developer content.
   Verify that the chosen theme appears in the table for the content type.
2. Write the deck to `presentation.md` using the Slide Structure and Standard Slide Template below.
   Verify with `head -n 5 presentation.md` that the front matter contains `marp: true`.
3. Apply best practices: concise titles, 3-5 bullets per slide, whitespace, and Marp image syntax.
   Verify with `grep -c '^---$' presentation.md` that slide separators exist, and review each slide against the Quality Checklist.
4. Render the deck with `marp presentation.md` (HTML) or `marp --pdf presentation.md`.
   Verify that `ls -l presentation.html presentation.pdf` shows a non-empty output file.
5. Deliver the saved `.md` file together with the rendered output.
   Verify that `ls presentation.md` lists the file at the path you report.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `marp: command not found` | Marp CLI is not installed | Run `npm install -g @marp-team/marp-cli`, then re-run the `marp` render command |
| Deck renders as one long page | Missing `marp: true` front matter | Add `marp: true` to the YAML front matter at the top of `presentation.md` and re-render |
| Image does not appear | Wrong relative path or image syntax | Fix the path relative to `presentation.md` and use the Marp bg image directive with a relative path |
| PDF export fails | No Chrome or Chromium available to Marp | Install Chromium or set `CHROME_PATH`, or export HTML instead with `marp presentation.md` |

## Slide Structure

```markdown
---
marp: true
theme: default
paginate: true
---

<!-- _class: lead -->
# Main Title
## Subtitle or Speaker Name

---

## Slide Heading

- Key point one
- Key point two
- Key point three

---

## Slide with Side Image

![bg right:40%](diagram.png)

- Explanation point 1
- Explanation point 2
- Explanation point 3
```

---

## Core Marp Syntax

### Slide Separators

```markdown
---        # New slide
<!-- -->   # Blank slide comment
```

### Directives (Frontmatter)

```markdown
---
marp: true          # Required: enables Marp
theme: default      # Theme: default, gaia, uncover, or custom
paginate: true      # Show page numbers
header: "Title"     # Header text (all slides)
footer: "Company"   # Footer text (all slides)
---
```

### Slide-Scoped Directives

```markdown
<!-- _class: lead -->    # Apply class to this slide only
<!-- _paginate: false --> # Disable pagination on this slide
<!-- _header: "" -->     # Override header for this slide
```

### Image Syntax

```markdown
<!-- Full-page background -->
![bg](image.png)

<!-- Background, right half -->
![bg right:40%](image.png)

<!-- Background, left half -->
![bg left:30%](image.png)

<!-- Sized inline image -->
![w:600px](image.png)
![h:300px](image.png)

<!-- Multiple backgrounds (side-by-side) -->
![bg](img1.png)
![bg](img2.png)
```

### Typography and Emphasis

```markdown
**Bold**, *italic*, `code`

> Blockquotes for key messages

---
<br>      <!-- Extra spacing -->
```

---

## Content Best Practices

- **Slide titles**: Keep to 5-8 words max; avoid full sentences
- **Bullet points**: 3-5 items per slide maximum
- **Text density**: One concept per slide; break up walls of text
- **Visual hierarchy**: Use h2 for slide titles, h3 for sub-sections
- **Whitespace**: Generous spacing keeps slides readable
- **Consistency**: Same structure for all content slides

### Slide Types

1. **Title slide** — `<!-- _class: lead -->` + h1 + h2 subtitle
2. **Agenda/outline** — numbered list of sections
3. **Content slide** — h2 title + bullet points
4. **Image slide** — `![bg right:40%]` layout
5. **Quote slide** — blockquote on clean background
6. **Summary/CTA slide** — key takeaway + next steps

---

## Standard Slide Template

```markdown
---
marp: true
theme: default
paginate: true
---

<!-- _class: lead -->
# [Presentation Title]
## [Subtitle or Author · Date]

---

## Agenda

1. Topic One
2. Topic Two
3. Topic Three
4. Q&A

---

## [Section Title]

- Point one — concise, actionable
- Point two — specific, not vague
- Point three — parallel structure with above

---

<!-- _class: lead -->
# Thank You

Questions?

[contact@example.com](mailto:contact@example.com)
```

---

## Running and Exporting

### Preview

```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Preview in browser (live reload)
marp --preview presentation.md

# Or: Use Marp for VS Code extension
```

### Export

```bash
# Export to HTML
marp presentation.md

# Export to PDF
marp --pdf presentation.md

# Export to PowerPoint
marp --pptx presentation.md

# Export slides as PNG images
marp --images png presentation.md
```

---

## Quality Checklist

Before delivering slides, verify:

- [ ] Appropriate theme selected for audience/content
- [ ] Title slide uses `<!-- _class: lead -->`
- [ ] All slide titles are concise (5-8 words max)
- [ ] Bullet points are 3-5 items per slide
- [ ] Images use correct Marp syntax
- [ ] Pagination enabled in frontmatter
- [ ] Logical flow: intro → body → conclusion

---

## References

- [Marp Official Site](https://marp.app/)
- [Marp CLI](https://github.com/marp-team/marp-cli)
- [Marpit Directives](https://marpit.marp.app/directives)
- [Marpit Image Syntax](https://marpit.marp.app/image-syntax)
- [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)
