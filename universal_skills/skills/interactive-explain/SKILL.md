---
name: interactive-explain
domain: development
skill_type: skill
description: Interactive codebase explanations
license: MIT
tags: []
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Interactive Explain

Generates interactive HTML/JS artifacts to explain logic or concepts.

## Capability

**generate_interactive_explanation** — produce a self-contained HTML/JS
explanation. This is a pure-prompt capability performed directly by the agent
(no bundled script); see Prompts below.

## Steps

1. Identify the concept or code to explain by reading the relevant source with `cat <file>`.
   Verify that you can state the logic in one sentence before designing the page.
2. Write a single self-contained HTML file such as `explain.html` following the Prompts below (vanilla JS, no external libraries).
   Verify with `grep -nE "<script src|<link .*href=\"http" explain.html` that nothing external is loaded.
3. Open the file in a browser or run `python3 -m http.server --directory <dir>` and load it.
   Verify that the page renders, the interactive controls respond, and the browser console shows no errors.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Page is blank | A JavaScript error stops the script | Open the browser console, fix the reported line in `explain.html` and reload |
| Page loads external assets | A CDN library or font was referenced | Remove the reference and replace it with inline vanilla JS and CSS |
| Controls do nothing | Event handlers bound before the DOM exists | Move the script to the end of `<body>` or wrap it in a `DOMContentLoaded` listener |

## Prompts
You are an expert at educational web design.
When generating interactive explanations:
1. Use modern CSS (gradients, shadows, glassmorphism).
2. Ensure the UI is responsive and "alive" with hover effects and transitions.
3. Use Vanilla JS only (no external libraries like React).
4. Focus on clarity and engagement.
