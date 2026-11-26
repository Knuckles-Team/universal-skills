---
name: jupyter-notebook
domain: system
skill_type: skill
description: >-
  Use when the user asks to create, scaffold, or edit Jupyter notebooks (`.ipynb`)
  for experiments, explorations, or tutorials; prefer the bundled templates and
  run the helper script `new_notebook.py` to generate a clean starting notebook.
license: MIT
tags: [jupyter, notebook, python, data-science, research]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# Jupyter Notebook

## Overview

- Experiments and exploratory analysis
- Tutorials and teaching-oriented walkthroughs

Prefer the bundled templates and the helper script for consistent structure and fewer JSON mistakes.

## When to use
- Create a new `.ipynb` notebook from scratch.
- Convert rough notes or scripts into a structured notebook.
- Refactor an existing notebook to be more reproducible and skimmable.
- Build experiments or tutorials that will be read or re-run by other people.

## Decision tree
- If the request is exploratory, analytical, or hypothesis-driven, choose `experiment`.
- If the request is instructional, step-by-step, or audience-specific, choose `tutorial`.
- If editing an existing notebook, treat it as a refactor: preserve intent and improve structure.

## Steps

1. Lock the intent by choosing the notebook kind, `experiment` or `tutorial`, and writing down the objective, audience and definition of done.
   Verify that the kind matches the Decision tree above.
2. Scaffold from the template with the helper script instead of hand-authoring raw notebook JSON.
   Verify that `ls output/jupyter-notebook/` lists the new `.ipynb` file.

```bash
uv run --python 3.12 python scripts/new_notebook.py \
  --kind experiment \
  --title "Compare prompt variants" \
  --out output/jupyter-notebook/compare-prompt-variants.ipynb
```

```bash
uv run --python 3.12 python scripts/new_notebook.py \
  --kind tutorial \
  --title "Intro to embeddings" \
  --out output/jupyter-notebook/intro-to-embeddings.ipynb
```

3. Fill the notebook with small, runnable cells, each focused on one step and preceded by a short markdown cell.
   Verify with `python3 -c "import json,sys; json.load(open(sys.argv[1]))" <notebook>.ipynb` that the file is still valid JSON.
4. Apply the right pattern from `references/experiment-patterns.md` or `references/tutorial-patterns.md`.
   Verify that the notebook follows the section order that reference describes.
5. When editing an existing notebook, make targeted edits and preserve the structure (read `references/notebook-structure.md` before touching raw JSON).
   Verify with `git diff --stat <notebook>.ipynb` that only the intended cells changed.
6. Run the notebook top to bottom with `jupyter nbconvert --to notebook --execute <notebook>.ipynb --output /tmp/check.ipynb` and walk the final pass in `references/quality-checklist.md`.
   Verify that the command exits 0, or say explicitly that execution was not possible and how to validate locally.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| `new_notebook.py` cannot find a template | Run from the wrong directory | Run it from this skill's directory so `assets/experiment-template.ipynb` resolves, or pass the absolute script path |
| `nbconvert` reports a missing kernel or module | `jupyterlab` and `ipykernel` are not installed | Run `uv pip install jupyterlab ipykernel`, then re-run the nbconvert command |
| Notebook fails to open after a raw edit | Invalid JSON from a hand edit | Validate with `python3 -c "import json,sys; json.load(open(sys.argv[1]))" <notebook>.ipynb`, fix the reported line using `references/notebook-structure.md` |

## Templates and helper script
- Templates live in `assets/experiment-template.ipynb` and `assets/tutorial-template.ipynb`.
- The helper script loads a template, updates the title cell, and writes a notebook.

Script path:
- `scripts/new_notebook.py` (relative to this skill's own directory)

## Temp and output conventions
- Use `tmp/jupyter-notebook/` for intermediate files; delete when done.
- Write final artifacts under `output/jupyter-notebook/` when working in this repo.
- Use stable, descriptive filenames (for example, `ablation-temperature.ipynb`).

## Dependencies (install only when needed)
Prefer `uv` for dependency management.

Optional Python packages for local notebook execution:

```bash
uv pip install jupyterlab ipykernel
```

The bundled scaffold script uses only the Python standard library and does not require extra dependencies.

## Environment
No required environment variables.

## Reference map
- `references/experiment-patterns.md`: experiment structure and heuristics.
- `references/tutorial-patterns.md`: tutorial structure and teaching flow.
- `references/notebook-structure.md`: notebook JSON shape and safe editing rules.
- `references/quality-checklist.md`: final validation checklist.
