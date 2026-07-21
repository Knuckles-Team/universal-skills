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
  version: '1.2.1'
  author: Genius
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

## Quality checks

- Give every section a unique job in advancing the thesis.
- Place definitions before dependent arguments and evidence beside the claim it supports.
- Remove repetition, orphan sections, and claims outside the audience promise.
- Keep the outline at planning granularity; do not hide a full draft inside it.
