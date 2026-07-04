# PARITY_MANIFEST — agent-package connector standard

**Golden reference:** `/home/apps/workspace/agent-packages/agents/gitlab-api`
(designated EXACT parity standard for all agent-package connector repos: file/folder
structure, GitHub workflows, configs).

This is the mechanical checklist a standardization pass applies to any connector repo
to verify/repair exact parity. Each row: file path → required/optional → content
pattern. Substitution variables are listed at the end.

Legend: **R** = required, **O** = optional (justified omission allowed), **G** = generated/local (never committed with secrets).

## 1. Root configuration files

| Path | Req | Content pattern |
|---|---|---|
| `pyproject.toml` | R | Golden shape: build-system `setuptools>=80.9.0` + `wheel`; `requires-python = ">=3.11, <3.15"`; deps `agent-utilities>=0.51.0` (+ `python-dotenv`, `gql[requests]` if GraphQL — the `requests` extra supplies `requests_toolbelt` needed by `gql.transport.requests`); `[[project.authors]]` table; `[project.license] text = "MIT"`; extras `mcp` / `agent` / (`gql`) / `all = ["{name}[mcp,agent,(gql,)logfire]>={version}"]` (self-referencing — bumpversion keeps the pin current) / `test`; `[project.scripts]` `{short}-mcp` + `{short}-agent`; `[tool.setuptools] include-package-data`; `[tool.setuptools.package-data] {pkg_dir} = ["mcp_config.json", "agent_data/**"]`; `[tool.setuptools.packages.find] where = ["."]`; `[tool.ruff]` line-length 88 / target py310; `[tool.ruff.lint]` select E,F,I,UP,B ignore E402,E501,B008; `[tool.mypy]` py 3.10 + ignore_missing_imports + check_untyped_defs; `[tool.vulture] ignore_names = ["request", "config"]`; `[dependency-groups] dev = ["pytest-timeout>=2.4.0"]`. License classifier: `"License :: OSI Approved :: MIT License"` (gitlab-api's stale `"License :: Public Domain"` was fixed in the 2026-06 golden-defect pass; see §8). |
| `.bumpversion.cfg` | R | Targets: `pyproject.toml` (`version = "…"` **and** a `[bumpversion:file(all-extra):pyproject.toml]` section for the self-referencing `{name}[…]>=…` `all`-extra pin), `a2a.json` (`"version": "…"`), `README.md` (`Version: …`), `docker/Dockerfile` (`{name}[all]>=…`), `{pkg_dir}/agent_server.py` + `{pkg_dir}/mcp_server.py` (`__version__ = "…"`). `commit = True`, `tag = True`. All seven targets must contain the current version or the pre-commit `check-bumpversion` hook fails. |
| `.pre-commit-config.yaml` | R | Byte-parity with golden: pre-commit-hooks v6.0.0 (incl. `no-commit-to-branch`, `check-added-large-files --maxkb=2000`); ruff-pre-commit **v0.15.12** (`ruff-check --fix --ignore=E402,B008,E501` + `ruff-format`); mirrors-mypy v1.20.2; vulture v2.16 (min-confidence 95); codespell v2.4.2 (`--ignore-words=.codespellignore`); bandit 1.9.4 (skip B101,B404,B603); nbQA 1.9.1; uv-pre-commit 0.11.8 (`uv-lock`); local hooks `check-mermaid`, `check-stubs` (agent-utilities scripts), `mermaid-validate` (node), `check-agent-standards` (agent_server must have `warnings.filterwarnings` + `file=sys.stderr`), `check-cli-help` (`uv run python -m … --help`), `mcp-readme-table` (`python -m agent_utilities.mcp.readme_tools` — regenerates the README MCP-tools table from the live server, CONCEPT:ECO-4.82), `check-bumpversion` (bump2version dry-run), `pytest` (`uv run --all-extras pytest … --timeout=60`); hadolint-py v2.14.0; docker-pre-commit v3.0.1 (`docker-compose-check`); local `verify-api-integration` (`scripts/verify_api_integration.py --local`) and `security-sanitizer` (`scripts/security_sanitizer.py`). |
| `pytest.ini` | R | `timeout = 60`, `asyncio_mode = auto`, `testpaths = tests`, `integration` marker excluded by default via `addopts = -m "not integration"`. Registers the `concept(id)` marker so `@pytest.mark.concept(...)` raises no unknown-marker warning under `--strict-markers` / `-W error` (concept-traceability parity). |
| `requirements.txt` | R | Mirrors `[project].dependencies` (one per line). |
| `uv.lock` | R | Committed; kept fresh by the `uv-lock` pre-commit hook. |
| `MANIFEST.in` | R | `include LICENSE` / `include README.md` / `include requirements.txt` / `recursive-include {pkg_dir} *.py *.json` — one directive per line (golden's formerly malformed single-line copy was fixed in the 2026-06 golden-defect pass; see §8). |
| `.gitignore` | R | Python packaging/caches + `.env`/`.venv` + `/site` + root-scratch guards: `/test_*.py /fix_*.py /debug_*.py /scratch_*.py /temp_*.py`, `*.orig *.rej *.patch *.log *output*.txt *errors*.txt failed_tests.txt trace.txt`. |
| `.gitattributes` | R | `* text=auto` + eol/diff mappings for sh/py/md etc. |
| `.dockerignore` | R | Excludes git/env/tests/scripts/.github/build, `{pkg_dir}.egg-info*`, plus `Dockerfile`, `debug.Dockerfile`, `compose.yml`. |
| `.codespellignore` | R | Word-per-line ignore list referenced by the codespell hook; grows per repo. |
| `.vulture_ignore` | R | Symbol-per-line list; pairs with `[tool.vulture]` in pyproject. |
| `.env.example` | R | Sectioned: MCP server settings (HOST/PORT/TRANSPORT), OTEL/Langfuse, Eunomia (`EUNOMIA_TYPE/POLICY_FILE/REMOTE_URL`), service credentials (`{SERVICE}_URL` / `{SERVICE}_TOKEN` commented), full `*TOOL` toggle list (one per MCP domain). |
| `.env` | G | Local copy of `.env.example`; git-ignored; never committed with real secrets. |
| `a2a.json` | R | A2A agent card: `name = "{name}-agent"`, `type = "agent"`, version (bumpversion-managed sync point), description, repo `url` (`https://github.com/Knuckles-Team/{name}/tree/main`), `license: MIT`, `capabilities[]` (incl. `run_graph_flow`), `tools[]` (incl. `graph-flow`). |
| `opencode.json` | R | `$schema https://opencode.ai/config.json`; lmstudio provider (`@ai-sdk/openai-compatible`, baseURL `http://vllm.arpa/v1`), model `lmstudio/qwen/qwen3.5-9b`. |
| `mcp_config.json` (root) | R | One `mcpServers` entry keyed `{name}`: `command: "uv"`, `args: ["run", "{short}-mcp"]`, env block with `<YOUR_…>` placeholders for `{SERVICE}_URL`/`{SERVICE}_TOKEN`/`{SERVICE}_SSL_VERIFY` + all `*TOOL` toggles. |
| `AGENTS.md` | R | Canonical agent guidance. Sections: Tech Stack & Architecture (+ mermaid architecture & workflow diagrams), Commands, Project Structure Quick Reference, Code Style, Dos and Don'ts, Safety & Boundaries, When Stuck, ⛔ No Scratch Files, ⛔ Root Pristine, Working Discipline, **Quality Bar (REQUIRED)**, **Working with Git Worktrees**. |
| `CLAUDE.md` | R | Pure stub: header + "canonical guidance lives in AGENTS.md" + `@AGENTS.md` import. No body content. |
| `README.md` | R | Title + badge block, `*Version: {version}*` line (bumpversion target), pointer to the GitHub Pages docs site, **Table of Contents**, overview, **## Key Features**, **## Available MCP Tools** section with the auto-generated table between `<!-- MCP-TOOLS-TABLE:START/END -->` markers (regenerated from the live server by the `mcp-readme-table` hook — do not hand-edit; CONCEPT:ECO-4.82), expanded **## Installation** (uvx, `pip install {name}` / `[all]`, console scripts `{short}-mcp` / `{short}-agent`), **## Usage** (Python API client / MCP-server CLI / action-routed tool-call code blocks), MCP env vars + stdio run snippet, and a **## Documentation** section linking the Pages site and `docs/` pages. Preserve the `<!-- BEGIN/END GENERATED: additional-deployment-options -->` marker block. (Documentation-governance A-grade baseline.) |
| `CHANGELOG.md` | R | Keep a Changelog 1.1.0 + SemVer; `## [Unreleased]` section maintained. |
| `LICENSE` | R | MIT. |
| `mkdocs.yml` | R | Material theme; `site_url https://knuckles-team.github.io/{name}/`; repo_name/repo_url `Knuckles-Team/{name}`; `edit_uri edit/main/docs/`; features incl. navigation.tabs/instant/footer, content.code.copy; 3-state palette (auto/light/dark, indigo); plugins `search`; markdown_extensions incl. pymdownx.highlight/inlinehilite/snippets/superfences(mermaid)/tabbed/emoji, admonition, attr_list, md_in_html, toc permalink; `extra.social` GitHub + PyPI; **nav exactly**: Home / Overview / Installation / Deployment / Usage (API / CLI / MCP) / Backing Platform ({Platform}) / Concepts. |

## 2. GitHub workflows (`.github/workflows/`)

| Path | Req | Content pattern |
|---|---|---|
| `pipeline.yml` | R | Name `Build\|Upload\|Release Python Package`; trigger `push: branches: ['main']`; job `publish-pypi` → `Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main` (secret `PYPI_API_TOKEN`); job `publish-docker` `needs: publish-pypi` → `container_pipeline.yml@main` (secrets `DOCKER_REGISTRY/USERNAME/PASSWORD/REPOSITORY`). **Pin `@main`, never `@latest`.** Docker build-cache config (org-wide `type=registry` cache convention, pipelines PR#1 — replaced the expiring `type=gha` SAS-token cache) lives inside the reusable `container_pipeline.yml`; per-repo workflows carry no cache config. Image name is `${DOCKER_USERNAME}/${repo-name}`. |
| `docs.yml` | R | Name `Deploy Documentation`; trigger push→main + `workflow_dispatch`; `permissions: contents: write`; single job: checkout@v4 (fetch-depth 0) → setup-python@v5 (3.12) → `pip install mkdocs-material` → `mkdocs gh-deploy --force`. |
| `pages.yml` | R | Name `Deploy GitHub Pages`; trigger push→main with paths filter `docs/**`, `mkdocs.yml`, `README.md`; job → `Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main`. Repo must have Pages enabled with `build_type=workflow`. |

## 3. docker/

| Path | Req | Content pattern |
|---|---|---|
| `docker/Dockerfile` | R | `# syntax=docker/dockerfile:1`; multi-stage: builder `python:3.11-slim` + `COPY --from=ghcr.io/astral-sh/uv:0.11.7`; `UV_COMPILE_BYTECODE/UV_LINK_MODE=copy/UV_SYSTEM_PYTHON/UV_HTTP_TIMEOUT=3600`; `RUN --mount=type=cache,target=/root/.cache/uv uv pip install --system --upgrade --break-system-packages --prerelease=allow {name}[all]>={version}` (bumpversion target); final stage copies `/usr/local`; ARG/ENV HOST/PORT/TRANSPORT/AUTH_TYPE; `CMD ["{short}-mcp"]`. |
| `docker/debug.Dockerfile` | R | Single-stage dev image: apt default-jre/ripgrep/tree/fd-find/curl/nano/build-essential/cmake/libssl-dev/pkg-config; installs uv + starship + rustup; `COPY . /app` + `uv pip install … .[all]`; `COPY docker/starship.toml /root/.config/starship.toml` (file must exist); `CMD ["{short}-mcp"]`. |
| `docker/agent.compose.yml` | R | Two services: `{name}-mcp` and `{name}-agent` (both `image: knucklessg1/{name}:latest`); agent `depends_on` mcp, `command: ["{short}-agent"]`, `MCP_URL=http://{name}-mcp:8000/mcp`, per-repo agent port; both: `env_file: ../.env`, `TRANSPORT=streamable-http` (mcp), `/health` python-urllib healthcheck, json-file logging 10m×3, `restart: always`. |
| `docker/mcp.compose.yml` | R | MCP service only — same `{name}-mcp` block as above (port 8000). |
| `docker/starship.toml` | R | Standard prompt config (copy golden verbatim). Located in `docker/`, not repo root. |

## 4. docs/ (published site — 7 pages, nav order canonical)

| Path | Req | Content pattern |
|---|---|---|
| `docs/index.md` | R | Hub: title, "Official documentation" admonition, PyPI/MCP/License/GitHub badges, overview, grid-cards linking the other pages. |
| `docs/overview.md` | R | Concept overview: category/role header, description, architecture, concept-registry table w/ inherited ECO-4.x rows, link to agent-utilities full registry. |
| `docs/installation.md` | R | Requirements (Python 3.11–3.14), PyPI install, extras table (mcp/agent/(gql)/all), from-source, Docker pull. |
| `docs/deployment.md` | R | **Four deployment options** in a marker-delimited (`<!-- BEGIN/END GENERATED: deployment-options -->`) `## Deployment Options` section — (1) stdio, (2) streamable-http, (3) local container/uv (`command: docker`/`podman` + local `url`), (4) remote `url` at `http://{name}-mcp.arpa/mcp` — as copy-paste `mcp_config.json`; plus `/health` check, Compose (`mcp.compose.yml` / `agent.compose.yml`), A2A agent server, Caddy + Technitium guidance. README carries a matching `### Additional Deployment Options` pointer (marker `additional-deployment-options`). Re-rendered by `scripts/standardize_deployment_docs.py`. |
| `docs/usage.md` | R | Same capability three ways: MCP tools (+ `*TOOL` toggles table), Python API (`get_client()`), CLI. |
| `docs/platform.md` | R/O | Backing-platform Docker recipe (the system the connector targets). Omit only for connectors of managed-only services (e.g. clarity-api) — document the omission. |
| `docs/concepts.md` | R | CONCEPT registry: `Prefix: CONCEPT:{PREFIX}-*`, version, ECO-4.0 bridge link, project-specific table (one row per MCP domain), cross-project references. |

## 5. scripts/ (repo validation; wired into pre-commit)

| Path | Req | Content pattern |
|---|---|---|
| `scripts/security_sanitizer.py` | R | Golden copy (generic). Called by the `security-sanitizer` pre-commit hook; blocks scratch/transient files and secret leaks. |
| `scripts/verify_api_integration.py` | R | Golden copy. Called by `verify-api-integration --local` hook; AST-maps MCP tools→API client methods and enforces the coverage baseline — add the repo to its `BASELINES` dict. |
| `scripts/validate_a2a_agent.py` | R | Golden copy; A2A endpoint smoke validator (adjust `A2A_URL` port). |
| `scripts/validate_agent.py` | R | Per-repo: imports the package's `agent_server` as a smoke test. |

## 6. Package layout (`{pkg_dir}/`)

| Path | Req | Content pattern |
|---|---|---|
| `__init__.py` | R | Dynamic exposure: `CORE_MODULES` (api) + `OPTIONAL_MODULES` (agent_server/mcp_server/gql) with `_MCP_AVAILABLE`/`_AGENT_AVAILABLE` flags; urllib3 warning filter. |
| `__main__.py` | R | Invokes `agent_server()`. |
| `agent_server.py` | R | `__version__` (bumpversion target); lazy `agent_utilities` imports inside `agent_server()`; `initialize_workspace()`/`load_identity()`; `warnings.filterwarnings` + startup print to `file=sys.stderr` (enforced by `check-agent-standards` hook); `create_agent_parser()`/`create_agent_server()`. |
| `mcp_server.py` | R | `__version__`; `get_mcp_instance()` returning `(mcp, args, middlewares)` via `create_mcp_server`. **Config + tool surface (ECO-4.82):** calls `load_config()` (NOT `load_dotenv`); the entire surface is wired by ONE shared call `register_tool_surface(mcp, service="{name}", client_cls=ApiClientSystem, get_client=get_client, tools_module=<pkg>.mcp)` (import the package as `from . import mcp as tool_modules` to avoid colliding with the local `mcp`). The helper owns `MCP_TOOL_MODE` (condensed default / verbose / both): it auto-discovers every `register_<domain>_tools` in the mcp package and gates each via `setting("<DOMAIN>TOOL", True)`, then adds the verbose 1:1 surface. Adding a domain = add `register_<domain>_tools` to `mcp/` + re-export in `mcp/__init__.py` (NO edit to `get_mcp_instance`). Multi-client agents pass `verbose_targets=[{client_cls,get_client,tool_prefix},…]`; codegen'd agents pass `tool_registry=TOOL_REGISTRY, manifest=OPERATIONS`. NO bare `os.getenv`, NO per-domain `if mode in (...)` branching in the agent. Transport dispatch stdio/streamable-http/sse; `--help` must work (`check-cli-help` hook). |
| `api_client.py` | R | Facade re-export from `api/` (backward compatibility). |
| `auth.py` | R | `get_client(url=None, token=None, verify=None, config=None)` singleton; credentials `{SERVICE}_URL`/`{SERVICE}_TOKEN`/`{SERVICE}_SSL_VERIFY` resolved via `config.setting(...)` at call time (one XDG config source; NOT import-time `os.getenv` defaults). **Two-tier auth (golden):** (1) **OIDC Delegation** (RFC 8693 token exchange) when `is_delegation_enabled(config)` — via `agent_utilities.mcp.delegated_auth` (`get_delegated_token`/`get_user_identity`/`is_delegation_enabled`); (2) fixed `{SERVICE}_TOKEN` fallback. Wraps `AuthError`/`UnauthorizedError` (from `agent_utilities.core.exceptions`) in `RuntimeError("AUTHENTICATION ERROR: …")`. Optional multi-tenant `instances.py` (CONCEPT:KG-2.9g) resolving a named instance from `<service>_instances` config — see `gitlab_api/instances.py`. |
| `api/__init__.py` + `api/api_client_base.py` + `api/api_client_{domain}.py` | R | Modular client mixins; base wraps requests.Session. |
| `mcp/__init__.py` + `mcp/mcp_{domain}.py` | R | One module per domain exposing `register_{domain}_tools(mcp)`; action-routed single tool per domain (`action` + `params_json` + `Field(...)`); lowercase tags; CONCEPT ID in docstring. **Action-router trio (golden):** `client=Depends(get_client)` (`fastmcp.dependencies.Depends`); `resolve_action(action, {…}, service="{name}")` + `run_blocking(client.method, **kwargs)` (both from `agent_utilities.mcp_utilities`); discovery payload returned when `resolve_action` yields a dict. |
| `{short}_input_models.py` | R | Pydantic input models (golden: `gitlab_input_models.py` — not `models.py`). |
| `{short}_response_models.py` | R | Pydantic response models. |
| `{short}_gql.py` | O | GraphQL wrapper (only for services with a GraphQL API; pairs with `gql` extra). |
| `mcp_config.json` | R | Package-level: `{"mcpServers": {}}` (shipped via package-data). |
| `main_agent.json` | R | Canonical StructuredPrompt (schema_version/task/type/source/instructions.core_directive/extends/tools). Validated by `prompt-builder/validate_prompt.py --strict` and `check_prompt_schema`. |
| `prompts/main_agent.json` + `prompts/__init__.py` | R | Same canonical prompt in the `prompts/` data subpackage = the `agent_utilities.prompt_providers` entry-point target (KG prompt-library discovery). Mirrors `main_agent.json` from ONE renderer (no drift). `__init__.py` makes it importlib-resolvable. |
| `skills/<pkg>-<category>/SKILL.md` (+ `skills/__init__.py`) | R | **Real per-tool-category skills** (one per MCP tool-category/workflow), NOT just a starter — house template (When to use / When NOT / Prerequisites / Tools & actions / Recipes / Gotchas / Related; see `servicenow-api/.../servicenow-incident-management`). Scaffold emits a `<short>-starter` placeholder; **replace it** with real skills before shipping. `agent_utilities.skill_providers` target. **Naming: every skill `name:` MUST be globally unique across the fleet and prefixed with the package slug (`<pkg>-…`)** — validated by `check_skill_name_collision.py`. Passes `check_atomicity`. |
| `prompts/<category>_specialist.json` | R | **≥1 domain-specialist StructuredPrompt** per tool-category persona (e.g. `incident_responder`, `cmdb_specialist`) beyond the generic `main_agent`: `task`,`type:"prompt"`,`schema_version:"1.0"`,`source:"{name}"`,`extends:"agent-utilities:base"`,`compose:"append"`,`identity`,`instructions`,`skills`,`tools` (scoped to that category). Validated by `validate_canonical(strict)`. Ships via the same `prompt_providers` entry-point. |
| `ontology/{domain}.ttl` + `ontology/__init__.py` | R | The package's **OWL/RDF ontology module** (CONCEPT:AU-KG.ontology.federation-provider-leg): classes/props in the SHARED `:` (`http://knuckles.team/kg#`) namespace; a per-package `owl:Ontology` IRI `http://knuckles.team/kg/{domain}` with `owl:imports <http://knuckles.team/kg>` (or `…/kg/enterprise` for EA/DB/governance). `__init__.py` is a data-only docstring. Federated into the KG hub via the `agent_utilities.ontology_providers` entry-point. **Do NOT redefine classes another package already owns** (e.g. `:MediaAsset`/`:Blob`/`:Document`/`:Person`) — reuse them. Scaffold with `scaffold_ontology_leg.py`, then hand-expand. Validated by `check_ontology.py`. |
| `kg_ingest.py` (record sources) / `kg_media.py` (producers) | R | **Native "maximum ingestion" into epistemic-graph** — the package pushes its OWN data into the KG in every modality that applies (CONCEPT:AU-KG.ingest.enterprise-source-extractor). Thin mapper over the shared primitive `agent_utilities.knowledge_graph.memory.native_ingest` (import GUARDED → no-op without it): `ingest_entities(entities, rels, source, domain)` (typed OWL nodes, ids `{domain}:{class}:{extId}`, `type` matching the `.ttl`), `ingest_documents(docs, source, domain)` (text → `:Document`), `media_store().store_media(bytes,…)` (raw bytes → `:Blob`+`:MediaAsset`). Dependency-/engine-guarded (clean no-op with no engine); reaches the engine via the lightweight client. Reference impls: `gitlab-api/kg_ingest.py`, `media-downloader/kg_media.py`. |
| Native-ingest MCP tool | R | A **Wire-First** tool (e.g. `{short}_ingest_<records>`) on the MCP surface that lists via the client and calls the `kg_ingest`/`kg_media` mapper — the live caller that makes ingestion reachable (two surfaces). |
| `connectors/mcp_source_presets.json` + `connectors/__init__.py` | R | In-repo Tier-1 `mcp_tool` source preset(s) (server + tool + field map) for hub-side pull ingestion, shipped via the `agent_utilities.source_connector_providers` entry-point (AU-KG.ingest.mcp-tool-connector). Complements the native push above. |
| `pyproject.toml` entry-points | R | ALL FOUR: `[project.entry-points."agent_utilities.skill_providers"]` + `…prompt_providers` + `…ontology_providers` + `…source_connector_providers`; package-data globs `prompts/**`,`skills/**`,`ontology/**`,`connectors/**`. |
| `tests/test_kg_ingest.py` (or `test_kg_media.py`) | R | Fakes-based Wire-First coverage of the record→entity/document/blob mapping (inject a fake engine client / MediaStore) + the no-op-without-engine guard. |
| `agent_data/` | O | Identity/workspace files (`IDENTITY.md`). Golden repo omits the directory but keeps the `agent_data/**` package-data glob — keep the glob either way. |

## 7. tests/ (flat pytest layout)

> **Every test function carries a concept marker.** Each test is decorated with
> `@pytest.mark.concept("{PREFIX}-001")` (registered in `pytest.ini`) and references
> `CONCEPT:{PREFIX}-001` in its docstring — the fleet convention that satisfies
> code-enhancer's concept-traceability domain at the A-grade baseline.

| Path | Req | Content pattern |
|---|---|---|
| `tests/__init__.py` | R | Empty. |
| `tests/conftest.py` | R | Shared fixtures (mock API client). |
| `tests/test_auth.py` | R | Auth error path raises `RuntimeError("AUTHENTICATION ERROR …")`. |
| `tests/test_api_wrapper.py` | R | API client request/response behavior (mocked session). |
| `tests/test_{short}_mcp_validation.py` | R | `get_mcp_instance()` registers tools. |
| `tests/test_init_dynamics.py` | R | Package import + `__all__` exposure. |
| `tests/test_startup.py` | R | Entry-point modules importable. |
| `tests/test_concept_parity.py` | R | `docs/concepts.md` exists, contains `ECO-4.0` bridge and the repo's `CONCEPT:{PREFIX}-` rows. |
| `tests/test_{short}_a2a_validation.py`, `test_mock_coverage.py`, brute-force coverage, model tests | O | Golden has them; add as the API surface grows. |

## 8. Known golden-repo deviations (adjudicate before copying)

Found during the 2026-06 audit (cross-checked vs twenty-mcp, kafka-mcp, clarity-api).
These were places where **gitlab-api itself** was stale or internally inconsistent.
Items 1–5 were **fixed in gitlab-api** by the 2026-06 golden-defect pass
(`fix/golden-standard-defects`); the notes below record the adjudication so the
defects are recognized if encountered in fleet repos:

1. **License classifier mismatch** — FIXED in golden. gitlab-api (and clarity-api)
   declared `"License :: Public Domain"` while `[project.license] text = "MIT"`.
   The standard (and the scaffold) is `"License :: OSI Approved :: MIT License"`;
   clarity-api still needs the same fix.
2. **`MANIFEST.in` malformed** — FIXED in golden. The file was a single line
   containing three directives; setuptools parses one directive per line. Golden and
   the scaffold now both use the multi-line form (incl. `include LICENSE`).
3. **`AGENTS.md` file tree was stale/machine-dumped** — FIXED in golden. The tree
   embedded `.mypy_cache/`/`.venv/` listings, named `docker/compose.yml` (actual:
   `agent.compose.yml`/`mcp.compose.yml`) and a 2-page `docs/`. Golden's tree now
   reflects git-tracked files only; keep generated trees pruned of caches/venvs.
4. **`all` extra self-pin** — drift risk FIXED in golden. Golden pins
   `all = ["gitlab-api[mcp,agent,gql,logfire]>={version}"]` (self-referencing);
   twenty-mcp/kafka-mcp instead pin upstream `agent-utilities[…]`. Golden is the
   designated standard, so the scaffold keeps the self-pin, and the pin is now a
   `.bumpversion.cfg` sync point (`[bumpversion:file(all-extra):pyproject.toml]`)
   so it can no longer drift.
5. **`a2a.json` placeholder URL/version** — FIXED in golden. The `url` was
   `https://github.com/user/gitlab-api/tree/main` ("user" org) and version `0.1.0`
   while the repo was at 25.x. Golden now uses the `Knuckles-Team` org URL and the
   real version, with `a2a.json` as a `.bumpversion.cfg` sync point (the
   new-connector convention, e.g. dockerhub-api).
6. **Pre-commit local hooks use absolute paths** —
   `/home/apps/workspace/agent-packages/agent-utilities/scripts/{mermaid_linter,check_stubs}.py`.
   Works fleet-wide on this infra; breaks for external contributors. Kept verbatim for
   parity.
7. **Fleet stragglers (for the standardization pass, not the scaffold)** — twenty-mcp
   is missing a2a.json/opencode.json/MANIFEST.in/pytest.ini/.codespellignore/uv.lock/
   debug.Dockerfile/agent.compose.yml/starship.toml/scripts/* and has a minimal
   pre-commit (ruff v0.3.4); kafka-mcp's pre-commit has only trailing-whitespace
   (v4.4.0) and its Dockerfile version pin (0.2.0) lags pyproject (0.6.0); twenty-mcp's
   Dockerfile pin (0.22.0) lags pyproject (0.31.0); kafka-mcp adds an extra
   `docs/architecture.md` page (acceptable superset); clarity-api omits opencode.json,
   .vulture_ignore (config lives in pyproject `[tool.vulture]` — acceptable),
   docs/platform.md (managed-only service), and the agent-validation scripts.

## 9. Per-repo substitution variables

| Variable | Derivation | Example (gitlab-api) |
|---|---|---|
| `{name}` | Repo / distribution name (kebab-case) | `gitlab-api` |
| `{pkg_dir}` | `{name}` with `-`→`_` | `gitlab_api` |
| `{short}` | `{name}` minus trailing `-mcp`/`-agent`/`-api` suffix | `gitlab` |
| `{short}-mcp` | MCP console script | `gitlab-mcp` |
| `{short}-agent` | Agent console script | `gitlab-agent` |
| `{Display Name}` | Title-cased name | `Gitlab Api` |
| `{description}` | One-liner; pattern `"{Platform} API + MCP Server + A2A Server"` | `GitLab API + MCP Server + A2A Server` |
| `{version}` | Current SemVer (bumpversion-managed, 7 sync points: pyproject version + `all`-extra self-pin, a2a.json, README, Dockerfile, agent_server, mcp_server) | `25.42.0` |
| `{SERVICE}_URL` / `{SERVICE}_TOKEN` / `{SERVICE}_SSL_VERIFY` | `{name}` upper-snake env prefix (preserve first-party names where they exist) | `GITLAB_URL` / `GITLAB_TOKEN` / `GITLAB_SSL_VERIFY` |
| `{PREFIX}` | CONCEPT ID prefix — check the registry in SKILL.md for collisions | `GL` |
| `{agent_port}` | Per-repo A2A agent port (compose + healthcheck) | `9017` |
| `{Platform}` | Backing-platform label in mkdocs nav / platform.md | `GitLab` |
| Docker Hub image | `knucklessg1/{name}:latest` | `knucklessg1/gitlab-api:latest` |
| GitHub org / Pages | `Knuckles-Team/{name}` / `https://knuckles-team.github.io/{name}/` | — |

## 10. Mechanical verification

Quick gate: run the drift-check script in SKILL.md Step 9. Deep audit: the
`ecosystem_standardizer` workflow. For byte-level parity of invariant files
(`.pre-commit-config.yaml`, the three workflows, `opencode.json`, `pytest.ini`,
`docker/starship.toml`), diff directly against the golden repo:

```bash
G=/home/apps/workspace/agent-packages/agents/gitlab-api
for f in .pre-commit-config.yaml .github/workflows/pipeline.yml \
         .github/workflows/docs.yml .github/workflows/pages.yml \
         opencode.json pytest.ini docker/starship.toml; do
  diff -q "$f" "$G/$f" || echo "DRIFT: $f"
done
```
