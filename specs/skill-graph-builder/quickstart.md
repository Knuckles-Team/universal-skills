# US-SKILL-GRAPH-BUILDER — Quickstart

Run the helper proofs:

```bash
uv run --all-extras pytest tests/test_skill_graph_builder.py -q
```

Build a graph from a local directory into a scratch folder:

```bash
python universal_skills/skills/skill-graph-builder/scripts/generate_skill.py ./docs demo --output-dir ./out
```
