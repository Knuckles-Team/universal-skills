# US-SKILL-GRAPH-BUILDER — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The CLI and its helpers exist and are tested. The pipeline behind them is the retired `agent_utilities` package, which is the real gap. The plan moves the pipeline into this repository, removes the daemon enrichment, and adds the ontology layer. Page fetch stays in the `web-crawler` skill.

## Technical Context

- **Language/Version**: Python 3.14, floor 3.12
- **Primary Dependencies**: the `web-crawler` skill, `markitdown`, `pymupdf4llm`
- **Storage**: files under the output directory
- **Testing**: pytest, `tests/test_skill_graph_builder.py`
- **Target Platform**: Linux, macOS and Windows paths
- **Project Type**: skill with a CLI script
- **Performance Goals**: N/A
- **Constraints**: flat hash-named `reference/`; paths within the constitution limits
- **Scale/Scope**: graphs up to about ten thousand pages

## Constitution Check

- R-I atomic skill: pass; the builder does one job.
- R-II legal paths: pass; the flatten step keeps names short.
- R-III scaffold: not applicable.

## Project Structure

```text
universal_skills/skills/skill-graph-builder/scripts/generate_skill.py   existing, edited
universal_skills/skill_graph_pipeline/                                  new package
tests/test_skill_graph_builder.py                                       new, bound rows
tests/test_skill_graph_builder_pipeline.py                              new, planned rows
tests/test_skill_graph_builder_served.py                                new, planned row
```

## Phase 0: Research

One unknown was resolved; see [research.md](research.md).

## Phase 1: Design

Data flow: `main` → `generate_skill` → `_classify_sources` → `SkillGraphPipeline.build` (acquire, normalize, split, write records) → `_flatten_reference_tree`. A `web` source runs `crawl.py` through `_make_crawler_fn`. The records and layout are the format of `SG-CONTENT`; see [contracts/graph-output.md](contracts/graph-output.md). The crawl seam is in [contracts/crawl-source.md](contracts/crawl-source.md). The served proof path is in [quickstart.md](quickstart.md).

Risk: the source kind `kg_query` stays in the closed set of `SG-CONTENT-R002.1`. Its acquisition moves to a served read when that operation is chosen. No row ships it before then.

## Phase 2: Task approach

Bound rows first. `R004.1` precedes `R003.*` because the records are written by the owned pipeline. `R004.2` follows the engine import row.

## Complexity Tracking

None.

## Build contract

Gates: `ruff`, `mypy`, `vulture`, `bandit`, `check-atomicity`, `check-frontmatter-portability`, `security-sanitizer`, `check-path-portability`. Test command: `uv run --all-extras pytest tests/test_skill_graph_builder.py -q`.

## Production caller chain

`python scripts/generate_skill.py <source> <name>` → `generate_skill` (`generate_skill.py`) → `_classify_sources` → `SkillGraphPipeline.build` → `_make_crawler_fn` → `skills/web-crawler/scripts/crawl.py` (for `web`) → `_flatten_reference_tree`. Obsolete paths to delete: the `agent_utilities` import, the flags `--no-kg`, `--ingest-kg`, `--append`, and the docs reference to the retired migration guide.

## Cross-repo seams

- Graph output: `SG-CONTENT-R002` checks what `R003.1` writes; see [contracts/graph-output.md](contracts/graph-output.md).
- Crawl source: `US-WEB-RESEARCH-R001.1` provides the page text; see [contracts/crawl-source.md](contracts/crawl-source.md).
