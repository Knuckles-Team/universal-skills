# Seam: crawl source

Provider: universal-skills US-WEB-RESEARCH-R001.1 (the `--output-dir` file output is added to that row when it lands)
Consumer: universal-skills US-SKILL-GRAPH-BUILDER-R002.2

## Wire shape

Request: `crawl.py --urls <url> --strategy recursive --output-dir <dir> --max-depth <n> --max-pages <n>`. Response: one markdown file per cited page, named `<sha256(url)[:8]>.md`, in the output directory. The served operation is `research.web` (`ARBORA-OPS-R067.1`).

## Refusal codes

`crawl.py` prints the operation refusal code and exits 2 (`US-WEB-RESEARCH-R001.4`). The builder stops on a non-zero exit.

## Authoritative types

`ResearchWebParams` and `ResearchWebResult` in `arbora/api/ops/research.py` of arbora.

## Test vectors

`tests/test_skill_graph_builder.py::test_web_sources_are_fetched_by_the_web_crawler_skill`.
