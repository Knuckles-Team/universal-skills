---
name: accessibility-audit
domain: web-development
skill_type: skill
description: >-
  Audit a rendered web interface for accessibility barriers with reproducible
  keyboard, screen-reader, responsive, and reduced-motion evidence. Use when
  reviewing an existing UI and prioritizing concrete accessibility fixes.
license: MIT
tags: [accessibility, ui-review, evidence]
metadata:
  version: '1.0.0'
  author: Agent Utilities Contributors
---

# Accessibility Audit

Review the user journeys and viewports in scope against the rendered interface, using the project's existing component and design system. The audit produces findings; it does not redesign the product or claim standards conformance from source inspection alone.

Exercise controls with keyboard alone and record focus order, visible focus, accessible names, error recovery, and status announcements. Check the same journeys at a narrow viewport and with reduced motion enabled. Use a screen reader when available, and identify any checks that were not observed. Automated accessibility scans can locate candidates but cannot establish that interaction and reading order work.

For each finding, report the route and control, an exact reproduction, expected and observed behavior, user impact, evidence from the rendered UI, and the smallest fix compatible with the existing component system. Rank blockers to task completion first. State the tested browser, viewport, assistive technology, and motion setting so another reviewer can repeat the result. Do not send UI content to an external service without the user's authorization.
