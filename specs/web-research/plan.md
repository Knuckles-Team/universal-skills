# US-WEB-RESEARCH — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

`universal_skills/skills/web-crawler/scripts/crawl.py` holds 1,360 lines of fetch, crawl and extraction code. `scripts/security_runtime.py` holds 478 lines of egress policy. `web-fetch` forwards to `web-crawler`. These scripts duplicate the connector path of `ARBORA-OPS-R067`.

## Architecture

Call path: skill script -> `arbora.client` -> served `research.web` -> engine search and selection -> connector fetch -> engine ingest.

The skill holds no rule and no state. It maps arguments and prints the result.

## Interfaces and data model

The skill arguments map onto `ResearchWebParams` of `ARBORA-OPS-R067.1`. The output is `ResearchWebResult` as JSON or as a text list.

## Live integration path

The skill scripts import only `arbora.client`, as the ecosystem boundaries allow for skill scripts.

## Quality and release gates

The repository pre-commit hooks and `tests/test_web_research_skill.py` must pass.

## Risks, alternatives, and decisions

The `--no-kg-ingest` file-only mode ends. Every run stores its pages through the platform.
