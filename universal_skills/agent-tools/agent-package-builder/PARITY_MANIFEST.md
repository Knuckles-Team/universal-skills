# Agent Package Builder — Current Parity Manifest

This manifest is the file-by-file contract for newly scaffolded provider packages.
`R` means required; `C` means conditional on a selected package type. Generated files
must remain environment-neutral, current-only, and deterministic.

## Root contract

| Path | Status | Contract |
|---|:---:|---|
| `pyproject.toml` | R | Python 3.12–3.14 with Ruff `py312` and mypy `3.12`; `agent-utilities[mcp]>=1.27.1,<2.0.0` and `epistemic-graph[full]>=2.23.1,<3.0.0` are direct dependencies. Extras are direct: `mcp` uses `agent-utilities[mcp]`; `agent` uses `agent-utilities[agent-runtime,logfire]`; `all` lists current upstream dependencies and never references the package itself. GraphQL adds `gql[requests]>=4.0.0`. Author metadata is the non-personal `Repository Maintainers`. The `[tool.pipelines_hooks.public_surface]` table declares the exact GitHub repository, PyPI distribution, Pages URL, and whether this package serves MCP. |
| `requirements.txt` | R | Exact newline rendering of `[project].dependencies`; no optional or recursive dependency. |
| `.bumpversion.cfg` | R | Version fields and installed Docker targets only; no self-referencing-extra target. |
| `.pre-commit-config.yaml` | R | Reviewed immutable hook revisions plus formatting, typing, tests, supply-chain, docs, privacy, skill, environment-drift, and generated-readme gates. The shared `public-surface` hook is pinned to pipelines commit `35209bf6d85569a3c1fe3d5cd31771cacfdc3731`. Scanner changed-source modes run at pre-commit; KISS/CCCC census and jscpd delta/census modes run only at pre-push/manual and CI. |
| `.cccc.toml`, `.kiss/kiss.toml`, `.importlinter` | R | Non-baseline structural policies: CCCC 10/15 caps, explicit KISS thresholds, and package-layer import contracts. Native tools are provisioned by the reviewed host/CI toolchain, never installed by hooks. |
| `scripts/check_scanners.py`, `scripts/run_kiss.sh` | R | Fail-closed wrappers for pinned CCCC/KISS/dupehound/import-linter checks, KISS/CCCC full censuses, and all-format jscpd delta/census. Changed-source checks run at pre-commit; tree work is pre-push/manual and CI only. Generated/vendor/fixture paths are excluded; Python is included in jscpd. These are source-checkout tools, retained in sdists but not runtime wheel data. |
| `.env.example` | R | Safe non-secret runtime switches and comments pointing to `AgentConfig`; no endpoint, credential, certificate, telemetry key, or TLS-verification value. |
| `.env` | — | Must not be generated or committed. |
| `mcp_config.json` | R | Installed stdio entry point, `MCP_TOOL_MODE=intent`, and non-secret tool toggles only. Provider values are resolved from `AgentConfig`. |
| `opencode.json` | R | Loopback-only neutral local-model example; no deployment hostname or credential. |
| `a2a.json` | R | Portable agent card with package metadata and no operator endpoint. |
| `README.md` | R | One-H1 public entry point with the required Overview, Key capabilities, Quick start, Architecture, Documentation, Development, and License headings; canonical GitHub/PyPI badges plus the MCP badge only when configured; a public Pages link; generated tool and MCP-example markers; current extras; mandatory full graph engine; least-privilege stdio container; authenticated HTTPS network boundary; AgentConfig/TLS references; 1,500–24,000 characters and at most 200 lines. |
| `AGENTS.md` | R | Current-state contributor contract with the durable What this repository owns, Architecture and module map, Commands, Quality gates, Development rules, Documentation, and Branching & isolation headings; no local paths or planning/history language; 1,200–24,000 characters and at most 240 lines. |
| `CLAUDE.md` | R | Stub importing the canonical `AGENTS.md`. |
| `LICENSE` | R | MIT license using `Repository Maintainers`, never a person's identity. |
| `CHANGELOG.md` | R | Keep a Changelog structure. |
| `MANIFEST.in` | R | Includes prompts, skills, ontologies, connector presets, package MCP config, and the scanner policies/wrappers needed to recreate the source-checkout quality surface from an sdist. Runtime wheels/images do not install scanner binaries. |
| `pytest.ini` | R | Unit tests by default; explicit integration marker. |
| `.gitignore`, `.gitattributes`, `.dockerignore`, `.codespellignore`, `.vulture_ignore` | R | Portable repository hygiene; `.env` remains ignored even though it is never generated. |

## Runtime and container contract

| Path | Status | Contract |
|---|:---:|---|
| `docker/Dockerfile` | R | The workspace compatibility-matrix authority pins Python 3.12 slim at `sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de`; `mcp` target installs `[mcp]`; `agent` target installs `[agent]`. Both contain mandatory `epistemic-graph[full]`; only the optional agent orchestration stack differs. |
| `docker/debug.Dockerfile` | R | Digest-pinned development image with no network-to-shell installer. |
| `docker/mcp.compose.yml` | R | Immutable image input, loopback publication, configured authentication for network mode, and read-only operator AgentConfig mount; no `env_file`. |
| `docker/agent.compose.yml` | R | Same controls for MCP and agent services; internal service traffic may use container-local HTTP, while external traffic requires authenticated TLS ingress. |
| `docker/starship.toml` | R | Presentation-only shell configuration. |
| `.github/workflows/pipeline.yml`, `.github/workflows/pages.yml` | R | Reusable workflows pinned to reviewed commit digests. |
| `.github/workflows/scanners.yml` | R | Dedicated CI source-checkout gate: provisions exact CCCC 1.6.0, KISS 0.4.10, dupehound 0.1.2, jscpd 5.0.16, and import-linter 2.14 versions, asserts the checked-in profile, and runs changed-source, pre-push delta, and KISS/CCCC/jscpd census modes. No hook-time installation or permanent baseline. |

## Documentation contract

| Path | Status | Contract |
|---|:---:|---|
| `mkdocs.yml` | R | Strict Material build with all seven pages in navigation. |
| `docs/index.md` | R | Package purpose and AgentConfig activation model. |
| `docs/overview.md` | R | Intent-routed architecture and inherited concept links. |
| `docs/installation.md` | R | Separate core, MCP, and agent installs; current bounded dependencies; immutable container digest. |
| `docs/deployment.md` | R | Local stdio/loopback, least-privilege stdio container, and authenticated HTTPS remote contract. No environment-specific proxy, DNS name, plaintext remote endpoint, raw provider value, or generated `.env`. |
| `docs/usage.md` | R | `get_client()` resolves `provider_configs.<provider>` through AgentConfig. No shell exports of endpoint or credentials. |
| `docs/platform.md` | R | Neutral out-of-the-box backing-system guidance only; no customized ontology or environment profile. |
| `docs/concepts.md` | R | Package concepts and inherited ecosystem bridges. |
| `docs/agent-readiness.json` | R | Explicit applicability, capability evidence, maturity labels, budgets, and Content Signals policy. No inferred capability or private value. |
| `docs/agent-readiness.schema.json` | R | Versioned machine-readable contract copied from the builder authority, including exact optional RFC 8414/9728 well-known metadata bindings. |
| `llms.txt`, `llms-sections/<slug>/llms.txt` | R | Deterministic, current-only, bounded discovery indexes generated from exact MkDocs nav and source Markdown. |
| `llms-full.txt` | C | Optional full current-Markdown context; emitted only with an explicit bounded budget. |
| `markdown-mirror-manifest.json`, `agent-readiness-manifest.json` | R | Raw Markdown mapping (canonical route plus explicit `index.md` fallback) and sorted provenance/applicability digests generated by the readiness tool. |
| `.well-known/api-catalog` | C | RFC 9727/RFC 9264 `application/linkset+json` linkset containing only validated, relative package authorities; never runtime endpoints. |
| `.well-known/mcp-server-card.json` | C | Versioned experimental MCP Server Card emitted only when the bound MCP capability artifact proves HTTP transport support; no endpoint or credential claims. |
| `.well-known/agent-skills.json` | C | Versioned Agent Skills index emitted only for regular, bound `SKILL.md` files under the validated package skills path. |

## Python package contract

| Path | Status | Contract |
|---|:---:|---|
| `<pkg>/__init__.py` | R | Current optional-module discovery without legacy aliases. |
| `<pkg>/auth.py` | R | `resolve_provider_runtime_profile` boundary; reference-only endpoint/credentials; exact TLS profile; optional OIDC delegation; no raw URL/token/verify arguments. |
| `<pkg>/error_authority.py` | R | Framework-neutral RFC 9457 authority shared by HTTP/MCP adapters: negotiates `application/problem+json` and structured `text/markdown`, retains browser `text/html`, sanitizes and bounds detail, and makes intentional denials non-retryable. |
| `<pkg>/api/` | R | Canonical public API package with URL/origin validation, finite bounds, redirect rejection, `ResolvedTLSProfile`, and no top-level facade. |
| `<pkg>/mcp/` | R | Atomic intent-routed domains with bounded inputs and globally unique provider-prefixed names. |
| `<pkg>/mcp_server.py` | C | `load_config`, governed server factory, one `register_tool_surface` call, default `intent` mode. |
| `<pkg>/agent_server.py`, `<pkg>/__main__.py` | C | Current `agent-runtime` entry point and canonical structured prompt. |
| `<pkg>/<short>_gql.py` | C | GraphQL transport configured by the same resolved TLS profile; bounded query input. |
| `<pkg>/main_agent.json`, `<pkg>/prompts/` | R | Canonical structured prompts with no local path or deployment identity. |
| `<pkg>/skills/` | R | At least one atomic, provider-prefixed, portable skill. |
| `<pkg>/ontology/` | R | Out-of-the-box provider semantics only; custom schemas are discovered or mapped at runtime. |
| `<pkg>/connectors/mcp_source_presets.json` | R | Neutral presets with explicit operator mapping placeholders. |
| `<pkg>/kg_ingest.py` | R | Direct native-ingest integration; no no-engine compatibility branch. |
| `<pkg>/mcp_config.json` | R | Packaged empty multiplexer config. |
| `<pkg>/<short>_input_models.py`, `<pkg>/<short>_response_models.py` | R | Typed domain boundary models. |

## Tests and scripts

| Path | Status | Contract |
|---|:---:|---|
| `tests/test_auth.py` | R | Reference resolution, fixed/delegated auth, redacted failures, TLS-profile lifetime. |
| `tests/test_api_wrapper.py` | R | Origin, redirect, timeout, and response-size boundaries using a resolved TLS profile. |
| `tests/test_error_authority.py` | R | JSON/Markdown metadata parity, browser HTML retention, bounded privacy-safe detail, and denial non-retryability. |
| `tests/test_kg_ingest.py` | R | Fakes-based mapping verification against the mandatory native ingestion primitive. |
| `tests/test_<short>_mcp_validation.py` | C | Governed server and intent tool registration. |
| `tests/test_startup.py`, `tests/test_init_dynamics.py`, `tests/test_concept_parity.py` | R | Import, entry-point, and concept gates. |
| `scripts/security_sanitizer.py`, `scripts/verify_api_integration.py`, `scripts/validate_a2a_agent.py`, `scripts/validate_agent.py` | R | Bounded, non-secret validation helpers copied from reviewed templates. |
| `scripts/generate_agent_readiness.py` | R | Deterministic source-Markdown generator; no provider imports or generated-HTML scraping. |
| `scripts/agent_readiness_tck.py` | R | Bounded served-surface TCK adapter with explicit HTTPS-origin allowlisting, fixture-only local mode, no credentials, rejected redirects, negotiated Markdown/HTML and RFC 9457 parity checks, discovery validation, budgets, and explicit unavailable/not-applicable evidence. |

## Current-only rejection gate

A scaffold fails parity if it contains any of the following:

- `agent-utilities` below `1.27.1`, the retired `agent` extra, or a recursive `all` extra;
- anything other than mandatory `epistemic-graph[full]` for the engine dependency;
- a generated `.env`, raw credential/endpoint/certificate value, `SSL_VERIFY`, or
  `verify=False` path;
- a legacy import facade, retired MCP mode alias, or no-engine compatibility branch;
- a mutable production image tag, unauthenticated non-loopback listener, plaintext remote
  MCP URL, or named proxy/DNS assumption;
- a person's name, email, real local path, or environment-specific connection profile.
