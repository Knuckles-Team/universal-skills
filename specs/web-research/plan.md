# US-WEB-RESEARCH — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The web-crawler skill becomes a thin shell over the served operation `research.web` (ARBORA-OPS-R067), and web-fetch forwards to it. The live caller is `main` (universal_skills/skills/web-crawler/scripts/crawl.py:946). The reuse candidate is the arbora client `invoke`; all fetch, render, crawl and extraction code is deleted.

## Technical Context

- **Language/Version**: Python 3.14 standard, 3.12 floor (requires-python >=3.12)
- **Primary Dependencies**: The arbora Python client (`arbora.client`); no HTTP client, browser driver or HTML parser in the skill
- **Storage**: N/A
- **Testing**: pytest (`uv run pytest`) with the tests named in the rows
- **Target Platform**: Linux, macOS and Windows developer machines and CI
- **Project Type**: skill library
- **Performance Goals**: N/A (one operation call per run)
- **Constraints**: No local page fetch, render, crawl or extraction code; the only network call is `research.web`; a refusal exits 2 with no fallback
- **Scale/Scope**: 5 active rows over two skills; crawl.py shrinks from 1,360 lines to a thin shell and security_runtime.py is deleted

## Constitution Check

- I One owner per concept: pass. Each row names one owning file.
- II Extend before you create: pass. Each `Shape:` sentence names the helper to reuse.
- XXIV Complete rows: pass. Every active row holds a caller chain, a shape and a test reference.
- XI Code stays small: pass. The Build contract lists the complexity and size limits.
- XXI Public files stay portable: pass. The spec holds no host data and no local path.
- R-I A skill is atomic and portable: pass. Each skill does one job with portable frontmatter.
- R-II Paths are legal on every platform: pass. New paths stay within the length limits.

## Project Structure

Paths this spec owns:

```text
universal_skills/skills/web-crawler/SKILL.md                  existing  rewritten to the operation call
universal_skills/skills/web-crawler/scripts/crawl.py          existing  reduced to a thin shell
universal_skills/skills/web-crawler/scripts/security_runtime.py existing  deleted
universal_skills/skills/web-fetch/scripts/fetch.py            existing  forwards to crawl.py
tests/test_web_research_skill.py                              new       unit tests
tests/test_web_research_skill_served.py                       new       served hot-path proof
tests/test_web_crawler_security.py                            existing  deleted with the code it covers
```

## Phase 0: Research

No unknowns. The operation name, its owner row and the client call are known; this spec adds no research.md.

## Phase 1: Design

The skill holds no fetch code. The sections below keep the existing design notes.

### US-WEB-RESEARCH — Design and implementation plan

Governing spec: [spec.md](spec.md).

### Existing system and reuse

`universal_skills/skills/web-crawler/scripts/crawl.py` holds 1,360 lines of fetch, crawl and extraction code. `scripts/security_runtime.py` holds 478 lines of egress policy. `web-fetch` forwards to `web-crawler`. These scripts duplicate the connector path of `ARBORA-OPS-R067`.

### Architecture

Call path: skill script -> `arbora.client` -> served `research.web` -> engine search and selection -> connector fetch -> engine ingest.

The skill holds no rule and no state. It maps arguments and prints the result.

### Interfaces and data model

The skill arguments map onto `ResearchWebParams` of `ARBORA-OPS-R067.1`. The output is `ResearchWebResult` as JSON or as a text list.

### Live integration path

The skill scripts import only `arbora.client`, as the ecosystem boundaries allow for skill scripts.

### Quality and release gates

The repository pre-commit hooks and `tests/test_web_research_skill.py` must pass.

### Risks, alternatives, and decisions

The `--no-kg-ingest` file-only mode ends. Every run stores its pages through the platform.

## Phase 2: Task approach

Order the work producer first: write the thin shell and its unit tests, then delete the local code, then forward web-fetch, then the served proof. Each task line in tasks.md names one row.

## Complexity Tracking

None. The constitution check passed with no violation.

## Build contract

The change must meet these gate thresholds from the organization constitution table.

- Cyclomatic complexity 10 and cognitive complexity 15 per function (`pipelines_hooks/complexity`).
- Words per sentence 20 (`ste`).
- Clone similarity 0.85 blocking at 40 tokens (`dupehound`).
- KISS limits from `.config/kiss.toml`: 35 statements, 15 locals, 20 calls, 3 positional arguments, 4 indentation levels, 300 lines and 10 functions per file.
- Pre-land fast set: `format`, `hygiene`, `secrets`, `types`, `tests-fast`; post-land set: `spec`, `tests`, `supply-chain`.

Repository commands: `uv run pytest` for the tests named in the rows and `pre-commit run --all-files` for ruff, mypy, vulture, codespell and bandit.

No scanner gaming, no suppression and no duplicate implementation: a row reuses the helper named in its `Shape:` sentence.

## Production caller chain

Entry point: an agent follows universal_skills/skills/web-crawler/SKILL.md and runs `crawl.py`; `main` (universal_skills/skills/web-crawler/scripts/crawl.py:946) will call `invoke` of the arbora client with the operation `research.web`. `web-fetch` reaches it through `main` (universal_skills/skills/web-fetch/scripts/fetch.py:48). Obsolete paths to delete: the local crawler in crawl.py, security_runtime.py and tests/test_web_crawler_security.py.

## Cross-repo seams

None. Arbora owns the operation `research.web` through ARBORA-OPS-R067; the skill only calls it.
