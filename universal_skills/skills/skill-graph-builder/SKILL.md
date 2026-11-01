---
name: skill-graph-builder
domain: agent-tools
skill_type: skill
description: >-
  Pointer for building a standardized agent skill-graph from a documentation
  source. Use to learn where skill-graph import and validation live today; the
  distillation pipeline has no runtime home yet.
license: MIT
tags: [skill-graph, builder, automation, docs, skill, generator, transformation]
metadata:
  version: '1.5.2'
  author: Genius
---

# Skill-Graph-Builder

A skill-graph is a corpus of knowledge packaged as an agent skill: a `SKILL.md`
index over a `reference/` markdown tree.

The distillation pipeline that this skill drove had no home after the
agent-utilities split, so the builder script is removed. Medulla validates and
imports finished skill-graph bundles: `MEDULLA-TYPED-PACKS-R700` and its
children. Native distillation of a source into such a bundle is filed as
`MEDULLA-TYPED-PACKS-R700.7`, and it will be served through arbora.

Until that row lands, author the bundle by hand to the layout in
[STANDARDS.md](../../../STANDARDS.md) and import it with the pack import
operation.
