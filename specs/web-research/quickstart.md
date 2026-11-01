# US-WEB-RESEARCH quickstart

Run the proofs from the repository root.

## Unit tests

```bash
uv run pytest tests/test_web_research_skill.py
```

Expected once built: the call mapping, the absence of an HTTP client, the web-fetch forward and the refusal exit pass.

## Served hot path (R001.5)

```bash
uv run pytest tests/test_web_research_skill_served.py
```

Expected once built: the fixture arbora server receives one `research.web` call and the skill makes no other network request.
