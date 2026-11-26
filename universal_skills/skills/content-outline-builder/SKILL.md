---
name: content-outline-builder
domain: content
skill_type: skill
description: >-
  Turn an approved content brief and source packet into a structured, evidence-aware
  outline with a thesis, section purposes, claim placement, and source mapping. Use
  when a user has a topic, audience, objective, and research but needs the argument
  organized before drafting. Do not use to research sources, write the full draft,
  or publish content.
license: MIT
tags: [content, outline, editorial, structure, evidence]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Content Outline Builder

Create one outline from the supplied brief and evidence. Preserve uncertainty and
leave unsupported claims visibly unresolved.

## Required inputs

- Audience, objective, channel or format, target length, voice, and call to action.
- Approved source packet with stable source identifiers.
- Mandatory points, prohibited claims, and publication constraints.

If an input is missing, mark it as an open question. Do not invent research to fill
the gap.

## Output contract

Return:

- Three title options and one-sentence audience promise.
- Thesis and the logical progression that supports it.
- Ordered sections with purpose, key claims, source IDs, suggested evidence, and
  transition intent.
- Opening and closing strategy, call to action, and optional visual opportunities.
- Open questions, unsupported claims, and scope cuts needed to meet the target length.

Map each factual claim to at least one source ID. Label interpretation, prediction,
and opinion distinctly from sourced fact.

## Steps

1. Check that the brief and source packet are complete.
   Run `ls` on the supplied files. Verify that audience, objective, format, length, voice, and call to action are each present or listed as open questions.
2. State the thesis and the logical progression.
   Run `grep -n -i "thesis" outline.md`. Verify that the thesis is one sentence and every section below traces to it.
3. Build ordered sections with purpose, key claims, source IDs, evidence, and transition intent.
   Verify that `grep -c "Source IDs" outline.md` equals the number of sections.
4. Map each factual claim to a source ID and label interpretation, prediction, and opinion.
   Run `grep -n "UNSUPPORTED" outline.md`. Verify that every unmapped claim appears in the open-questions list.
5. Run the quality checks and finish the output contract.
   Run `grep -c -i "title option" outline.md`. Verify that there are three title options, a closing strategy, and scope cuts, and that no full draft prose is embedded.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A claim has no source ID | Source packet does not cover it | Mark it unsupported in open questions and do not research new sources |
| Two sections do the same job | Overlapping scope | Merge them or reassign claims so each section has a unique purpose |
| Outline overshoots target length | Too many sections for the word budget | List scope cuts in the output and drop the weakest section |

## Quality checks

- Give every section a unique job in advancing the thesis.
- Place definitions before dependent arguments and evidence beside the claim it supports.
- Remove repetition, orphan sections, and claims outside the audience promise.
- Keep the outline at planning granularity; do not hide a full draft inside it.
