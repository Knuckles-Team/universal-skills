---
name: pre-mortem
description: >-
  Gary Klein's and Daniel Kahneman's 30-year-old prospective hindsight technique to stress-test high-stakes decisions by time-traveling 6 months into the future when the plan is dead, reverse-engineering failure modes, spawning parallel investigators, and synthesizing revised plans/checklists.
categories: [Productivity]
tags: [pre-mortem, planning, risk-analysis, decision-making, strategy]
license: MIT
metadata:
  author: Genius
  version: '0.42.1'
---
# Pre-Mortem Skill (pre-mortem)

Stress-test plans and design documents using Gary Klein's "prospective hindsight" technique. Time-travel 6 months into the future to a state where your plan has failed completely, reverse-engineer why it failed, spawn parallel investigators to analyze each failure, and synthesize early warning signs, a revised plan, and a pre-launch checklist.

---

## Overview

A pre-mortem is one of the most powerful risk mitigation tools available. It operates under a simple cognitive shift: **instead of asking "what might go wrong?", you state "it is 6 months in the future, and this project has completely failed. Let's write the history of that failure."**

This cognitive shift bypasses groupthink, unlocks creative skepticism, and exposes deep, unexamined assumptions before a single line of code is written or deployed.

---

## Steps

### Step 1: gather_context
The agent scans the active conversation and the local workspace (including design documents, plans, and configuration files) to build a comprehensive understanding of the proposed plan:
- Determine the scope, target audience, execution steps, technology stack, and success criteria.
- If the current context is insufficient to conduct a rigorous pre-mortem, the agent must ask highly focused, sequential questions (one at a time) to extract the necessary plan details. No pre-existing brief is required.

### Step 2: failure_generation [depends_on: gather_context]
The agent shifts the cognitive frame: **"It is 6 months in the future. The plan has failed catastrophically. It is a smoking ruin."**
- Generate a list of realistic, distinct failure modes (typically 4 to 9 depending on the complexity of the plan).
- Each failure mode must be genuine, specific to the plan, and cover technical, operational, organizational, or dependency failures. Avoid generic or superficial answers.

### Step 3: parallel_investigators [depends_on: failure_generation]
For each generated failure mode, the agent spawns (or simulates the parallel execution of) independent specialized sub-agent investigators:
- Each investigator goes deep into its assigned failure mode.
- Each investigator produces:
  1. **A detailed case study** of how this specific failure played out step-by-step.
  2. **The single biggest hidden assumption** that enabled this failure.
  3. **Early warning signs** (telemetry, metrics, behavioral indicators) that would be visible weeks before the crash.

### Step 4: synthesis [depends_on: parallel_investigators]
The agent compiles and synthesizes the findings of the parallel investigators into a structured strategic output:
- **Most Likely Failure**: The failure mode with the highest probability that requires immediate, proactive changes.
- **Most Dangerous Failure**: The high-impact, existential failure mode that is worth purchasing insurance against, even if less likely.
- **Root Assumption**: The single most significant hidden assumption underpinning the original plan.
- **Revised Plan**: An actionable, updated version of the plan with specific, concrete changes mapped directly to the discovered failure modes.
- **Pre-Launch Checklist**: A list of 3-5 concrete, testable conditions that must be verified before shipping the plan.

### Step 5: visual_reporting [depends_on: synthesis]
The agent outputs the final pre-mortem results in two high-fidelity formats:
- **Visual HTML Report**: A premium, beautifully styled HTML document (rendered using premium CSS, curated dark palettes, elegant gradients, and clear typography) containing the synthesis and a summary of the investigator findings.
- **Markdown Transcript**: A clean, comprehensive markdown transcript detailing the full step-by-step reasoning of each parallel investigator.

---

## Visual Report Aesthetics

To wow the user and create a premium product feel, the Visual HTML Report should adhere to the following design aesthetics:
- **Color Palette**: Dark mode base (`#0f172a`, `#1e293b`) with vibrant, high-contrast semantic accents (e.g., deep ruby `#ef4444` for failures, glowing emerald `#10b981` for checklist items, and warm amber `#f59e0b` for assumptions).
- **Typography**: Modern typography utilizing premium Google Fonts (e.g., *Outfit* or *Inter*).
- **Interactive Elements**: CSS-based accordion drawers for case studies, interactive checkboxes for the pre-launch checklist, and sleek, glassmorphic container cards with subtle hover transitions.
- **Structure**:
  1. Header with plan name, version, and the simulated future failure date.
  2. A "Risk Profile Matrix" displaying the *Most Likely* vs. *Most Dangerous* failures.
  3. "The Investigators' Files" containing the detailed case studies and early warning signs.
  4. The "Revised Plan" showing side-by-side or clear diffs of modifications.
  5. The interactive "Pre-Launch Checklist".

---

## Best Practices

- **Avoid Complacency**: Do not list trivial or obvious failure modes (e.g., "the server ran out of disk space" unless it is highly probable). Push for nuanced architectural or social failure paths.
- **Prospective Hindsight Frame**: Ensure the language in Step 2 and Step 3 is strictly written in the **past tense** as if the failure has already occurred.
- **Actionability**: A pre-mortem is only valuable if it changes the current plan. The "Revised Plan" must have clear, tangible differences from the original.
