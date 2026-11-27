---
name: user-research
domain: research
skill_type: skill
description: >-
  Conducting user discovery, qualitative research, and persona development to
  understand customer needs and pain points. Use when preparing for discovery
  interviews, creating customer journey maps, mapping jobs-to-be-done (JTBD), or
  building proto-personas.
license: MIT
tags: [user-research, discovery, personas, jtbd, journey-mapping, qualitative]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# User Research & Discovery

Systematically uncover customer insights to ensure we build products that solve real problems.

---

## Steps

1. Write the interview guide to a file with `cat > research/interview-guide.md`, covering hypothesis, screener, opening, focus areas and closing. Verify that `grep -c -E "Hypothesis|Screener|Opening|Focus Areas|Closing" research/interview-guide.md` prints at least 5.
2. Draft the job statements in `research/jtbd.md` using the formula "When I [situation], I want to [motivation], so I can [expected outcome]". Verify that `grep -c "When I" research/jtbd.md` is at least the number of jobs you identified.
3. Build the proto-personas and journey map in `research/personas.md` after the interviews. Verify that `grep -n -E "Top Goals|Top Frustrations|Phases" research/personas.md` lists every persona and the journey phases.
4. Synthesize the memo into `research/memo.md` with themes, quotes and confidence scores. Verify that `grep -c -i "confidence" research/memo.md` is at least 1 and that every theme cites a quote.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Participants answer "yes" to everything | Leading questions such as "Would you use this?" | Rewrite them in `research/interview-guide.md` as "Tell me about the last time you tried to [action]" and re-run the affected interviews. |
| Personas read as demographics | Jobs were not mapped first | Go back to `research/jtbd.md`, state the functional, emotional and social job for each persona, then regenerate `research/personas.md`. |
| Insights rest on one or two interviews | Sample too small to support the theme | Mark the theme with a low confidence score in `research/memo.md` and schedule more interviews in the same segment. |

## 1. Discovery Interview Preparation

Before talking to users, define a structured research plan.

### Interview Guide Structure:
- **Hypothesis**: What single thing do we want to validate or invalidate?
- **Screener**: Who is the ideal participant? (Experience, role, behavior).
- **Opening**: Set context, assure anonymity, ask for permission to record.
- **Focus Areas**: 3–5 broad themes to explore.
- **Closing**: "Is there anything I should have asked but didn't?"

### The Golden Rule:
Ask open-ended questions. Avoid "Would you use this?" (leading). Prefer "Tell me about the last time you tried to [action]..." (experience-based).

---

## 2. Jobs-to-be-Done (JTBD)

Focus on the **task** the user is "hiring" the product to do, rather than their demographics.

**Formula**: "When I [situation], I want to [motivation], so I can [expected outcome]."

- **Functional Job**: The core task.
- **Emotional Job**: How the user wants to feel.
- **Social Job**: How the user wants to be perceived.

---

## 3. Personas & Journey Mapping

### Proto-Personas
Create lightweight, hypothesis-based profiles to align the team.
- **Name/Role**: "Small Business owner Sam".
- **Top Goals**: What are they trying to achieve?
- **Top Frustrations**: What blocks them today?
- **Behaviors**: How do they currently solve the problem?

### Customer Journey Mapping
Visualize the user's experience across touchpoints.
- **Phases**: Awareness → Discovery → Signup → Activation → Retention.
- **Actions**: What is the user doing at each step?
- **Thinking/Feeling**: What are the highlights and pain points?
- **Opportunities**: Where can we improve the experience?

---

## 4. Synthesis & Artifacts

- **Research Memo**: 1-page summary of key themes, supporting quotes, and recommended next steps.
- **Affinity Mapping**: Grouping observations into thematic clusters to identify patterns.
- **Confidence Scoring**: How sure are we of these insights based on the sample size/quality?

---

## Best Practices

- **Interview in Pairs**: One person leads, one person takes notes.
- **Record and Transcribe**: Don't rely on memory; use exact customer quotes.
- **Focus on Pain**: Users are great at describing problems but often bad at prescribing solutions. Focus on the pain.
- **Continuous Discovery**: Research isn't a one-time event; aim for a regular cadence of customer conversations.
