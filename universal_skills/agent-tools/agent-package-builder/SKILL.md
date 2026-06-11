---
name: agent-package-builder
description: >-
  Scaffold a complete agent-package project with all config files, Docker
  infrastructure, MCP server, A2A agent, and API client stubs. Use when creating a
  brand-new agent-package from scratch, bootstrapping a new MCP/agent/api-client
  project, or when the user says "create a new agent package". This delegates
  domain-specific implementation to existing skills (api-client-builder, mcp-
  builder, agent-builder, skill-graph-builder). Do NOT use for modifying an
  existing agent package — use the individual skills directly.
license: MIT
tags: [agent, package, scaffold, bootstrap, project, mcp, api-client, builder]
metadata:
  author: Genius
  version: '0.43.0'
---

# Agent Package Builder

Scaffolds a complete, production-ready agent-package project following the standardized ecosystem conventions. **The golden-standard reference repo is `agents/gitlab-api`** — a fresh scaffold must match its file/folder structure, GitHub workflows, and config shapes exactly. The definitive file-by-file checklist lives in [`PARITY_MANIFEST.md`](PARITY_MANIFEST.md) (sibling of this file); use it to verify a scaffold or to standardize an existing connector repo.

The generated project includes all hidden config files (`.pre-commit-config.yaml`, `.bumpversion.cfg`, `.gitignore`, `.gitattributes`, `.env` + `.env.example`, `.dockerignore`, `.codespellignore`, `.vulture_ignore`), Docker infrastructure (`docker/Dockerfile`, `docker/debug.Dockerfile`, `docker/agent.compose.yml`, `docker/mcp.compose.yml`, `docker/starship.toml`), the three GitHub workflows (`pipeline.yml`, `docs.yml`, `pages.yml`), Python packaging (`pyproject.toml`, `requirements.txt`, `MANIFEST.in`, `pytest.ini`), documentation (`README.md`, `CHANGELOG.md`, `AGENTS.md` + `CLAUDE.md` stub, `mkdocs.yml` + the 7-page `docs/` site), agent metadata (`a2a.json`, `opencode.json`, root + package `mcp_config.json`, `main_agent.json`), and repo validation scripts (`scripts/`). All state, logs, memory, and chat history are handled natively via the **Knowledge Graph**.

The bundled scaffolder does the mechanical work:

```bash
python3 scripts/scaffold_package.py <package-name> \
  [--type api_client,mcp,agent[,graphql]] [--concept-prefix XYZ] \
  [--display-name ...] [--description ...] [--output-dir ...] [--in-place]
```

---

## Workflow

### Step 1: gather-requirements

Collect the following from the user. Ask only for what is missing — do not re-ask for values already provided.

**Name availability gate (REQUIRED before anything is scaffolded):** the package
name must be the AVAILABLE name on PyPI — the published distribution name, the
GitHub repo name, and the DockerHub image name are all derived from it, so it is
solidified only after this check passes:

```bash
code=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/{package-name}/json")
[ "$code" = "404" ] && echo "AVAILABLE — name solidified" || echo "TAKEN — pick another name"
```

If taken, iterate with the user on a variant (suffix conventions in the fleet:
`-mcp` for MCP-centric connectors, `-api` for API-client-centric wraps,
`-agent` for agent-centric packages) and re-check until available.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `package-name` | ✅ | — | Kebab-case name (e.g., `jellyfin-mcp`) |
| `--display-name` | ❌ | Derived from package name | Human-readable name (e.g., `Jellyfin MCP`) |
| `--description` | ❌ | `"{Display Name} API + MCP Server + A2A Server"` | One-line description |
| `--type` | ❌ | `api_client,mcp,agent` | Comma-separated: `api_client`, `mcp`, `agent`, `graphql` |
| `--output-dir` | ❌ | Current directory | Where to create the project |
| `--author` | ❌ | `"Audel Rouhi"` | Author name |
| `--email` | ❌ | `"knucklessg1@gmail.com"` | Author email |
| `--service-url-env` | ❌ | `"{UPPER_NAME}_URL"` | Env var for the service URL |
| `--auth-env` | ❌ | `"{UPPER_NAME}_TOKEN"` | Env var for the auth token |
| `--concept-prefix` | ❌ | Derived from name | Unique CONCEPT ID prefix (e.g., `PORT` for portainer) |
| `--doc-urls` | ❌ | — | Comma-separated documentation URLs for skill-graph |

### Step 2: scaffold-tree [depends_on: gather-requirements]

Run `scripts/scaffold_package.py` (or generate the same set manually). The standard project structure — **exact gitlab-api parity** — is:

```
{project_dir}/
├── .bumpversion.cfg
├── .codespellignore
├── .dockerignore
├── .env                      # local copy of .env.example (git-ignored)
├── .env.example
├── .gitattributes
├── .github/
│   └── workflows/
│       ├── docs.yml          # mkdocs gh-deploy --force on push to main
│       ├── pages.yml         # reusable pages_pipeline.yml@main (docs/** path filter)
│       └── pipeline.yml      # reusable python_pipeline.yml + container_pipeline.yml @main
├── .gitignore
├── .pre-commit-config.yaml   # FULL gate — see PARITY_MANIFEST.md
├── .vulture_ignore
├── a2a.json                  # A2A agent card
├── AGENTS.md                 # canonical agent guidance (Quality Bar + worktree sections)
├── CHANGELOG.md              # Keep a Changelog
├── CLAUDE.md                 # 3-line stub importing @AGENTS.md — never holds content
├── LICENSE                   # MIT
├── MANIFEST.in
├── mcp_config.json           # root: uv-run launcher entry with env placeholders
├── mkdocs.yml                # Material theme, tabs nav, 7 pages
├── opencode.json
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt          # mirrors [project].dependencies
├── uv.lock                   # generate with `uv lock` (pre-commit uv-lock hook keeps it fresh)
├── docker/
│   ├── Dockerfile            # slim multi-stage, uv 0.11.7, cache mount
│   ├── debug.Dockerfile      # full dev image; COPY docker/starship.toml
│   ├── agent.compose.yml     # MCP + agent services (image knucklessg1/{name}:latest)
│   ├── mcp.compose.yml       # MCP service only
│   └── starship.toml
├── docs/
│   ├── index.md              # navigation hub w/ badges + grid cards
│   ├── overview.md           # concept overview / architecture
│   ├── installation.md       # pip / source / extras / docker
│   ├── deployment.md         # transports, compose, agent server, Caddy/Technitium
│   ├── usage.md              # API / CLI / MCP usage
│   ├── platform.md           # backing-platform deploy recipe
│   └── concepts.md           # CONCEPT ID registry
├── scripts/
│   ├── security_sanitizer.py        # pre-commit hook (bundled golden copy)
│   ├── verify_api_integration.py    # pre-commit hook (bundled golden copy)
│   ├── validate_a2a_agent.py        # A2A endpoint smoke validator
│   └── validate_agent.py            # agent entry-point import smoke test
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api_wrapper.py
│   ├── test_auth.py
│   ├── test_concept_parity.py
│   ├── test_init_dynamics.py
│   ├── test_startup.py
│   └── test_{short}_mcp_validation.py
└── {pkg_dir}/
    ├── __init__.py           # dynamic CORE/OPTIONAL module exposure
    ├── __main__.py           # invokes agent_server()
    ├── agent_server.py
    ├── api_client.py         # facade re-export from api/
    ├── auth.py               # get_client() singleton, std env var names
    ├── main_agent.json       # main-agent prompt definition
    ├── mcp_config.json       # package-level: {"mcpServers": {}}
    ├── mcp_server.py         # entrypoint (imports from mcp/)
    ├── {short}_gql.py        # GraphQL wrapper (graphql type only)
    ├── {short}_input_models.py
    ├── {short}_response_models.py
    ├── agent_data/
    │   └── IDENTITY.md       # optional — golden repo omits it; keep glob in package-data
    ├── api/
    │   ├── __init__.py
    │   ├── api_client_base.py
    │   └── api_client_{domain}.py
    └── mcp/
        ├── __init__.py
        └── mcp_{domain}.py
```

After scaffolding, run `uv lock` in the project — the pre-commit `uv-lock` hook and the `pytest` hook (`uv run --all-extras pytest …`) both expect `uv.lock` to exist.

#### Critical packaging requirements (these prevent real CI failures)

These were the exact causes of build/publish failures in the jena/kafka/camunda/archi
rebuilds. Bake them into every scaffold — a package that omits them looks fine locally
but reds the pipeline:

1. **`pyproject.toml` MUST follow the golden shape exactly.** Explicit package
   discovery (setuptools' flat-layout auto-discovery fails with sibling dirs
   `docker/`, `docs/`, `scripts/`, `tests/`), and the golden metadata conventions:
   ```toml
   [build-system]
   requires = [ "setuptools>=80.9.0", "wheel",]
   build-backend = "setuptools.build_meta"

   [project]
   # name/version/description/readme/classifiers …
   requires-python = ">=3.11, <3.15"
   dependencies = [ "agent-utilities>=0.47.0", "python-dotenv>=1.0.0",]

   [project.optional-dependencies]
   mcp = [ "agent-utilities[mcp]>=0.47.0",]
   agent = [ "agent-utilities[agent,logfire]>=0.47.0",]
   all = [ "{name}[mcp,agent,logfire]>=…",]   # self-referencing, bumpversion keeps in sync
   test = [ "pytest-xdist>=3.6.0", "pytest", "pytest-asyncio", "pytest-cov",]

   [tool.setuptools]
   include-package-data = true

   [tool.setuptools.package-data]
   {pkg_dir} = [ "mcp_config.json", "agent_data/**",]

   [tool.setuptools.packages.find]
   where = [ ".",]

   [tool.ruff]            # line-length 88, target py310
   [tool.ruff.lint]       # select E,F,I,UP,B; ignore E402,E501,B008
   [tool.mypy]            # 3.10, ignore_missing_imports, check_untyped_defs
   [tool.vulture]         # ignore_names request/config
   [dependency-groups]    # dev = pytest-timeout
   ```
   License classifier is `"License :: OSI Approved :: MIT License"` with
   `[project.license] text = "MIT"`. (gitlab-api's formerly stale
   `"License :: Public Domain"` classifier was fixed in the 2026-06 golden-defect
   pass; see PARITY_MANIFEST.md §8.)

2. **Naming MUST be consistent across all three identifiers — no deviations.**
   repo name (kebab) == distribution `name` (kebab) == package dir (snake_case).
   e.g. repo `jena-mcp` → `name = "jena-mcp"` → package `jena_mcp/`.
   NOT `apache-jena-mcp`/`apache_jena_mcp`; NOT `archimate_mcp` for repo `archi-mcp`.
   Console scripts strip the `-mcp`/`-agent`/`-api` suffix:
   `{short}-mcp = "{pkg_dir}.mcp_server:mcp_server"` and
   `{short}-agent = "{pkg_dir}.agent_server:agent_server"`
   (gitlab-api → `gitlab-mcp` / `gitlab-agent`).

3. **`docker/debug.Dockerfile` copies `docker/starship.toml` — the file must exist.**
   If it is missing the build dies with
   `failed to compute cache key: "/docker/starship.toml": not found`.
   The production `docker/Dockerfile` is a slim multi-stage build (uv `0.11.7`,
   `--mount=type=cache,target=/root/.cache/uv`, installs `{name}[all]>={version}` —
   the version pin is maintained by `.bumpversion.cfg`).

4. **Heavy / native-compiled deps MUST be optional extras + lazy-imported.** Libraries
   with C/build requirements (`confluent-kafka`/librdkafka, `rdkafka`, openblas) break
   manylinux/Windows wheel builds if placed in core `dependencies`. Put them under
   `[project.optional-dependencies]` (e.g. `native = ["confluent-kafka>=2.3.0"]`) and
   `import` them *inside* the function with `try/except ImportError` raising a clear
   "install `{repo}[native]`" message. Core deps stay `agent-utilities` (+ `requests`
   for HTTP API wrappers).

5. **New GitHub repos:** default branch must be `main` (not `master`); enable GitHub
   Pages with `build_type=workflow`
   (`POST /repos/{owner}/{repo}/pages -d '{"build_type":"workflow"}'`) or the `pages.yml`
   deploy fails with `Get Pages site failed ... HttpError: Not Found`. `.gitignore` must
   exclude `build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .mypy_cache/` plus the
   root-scratch patterns (`/test_*.py`, `/fix_*.py`, `*.log`, …).

6. **Workflows pin the reusable pipelines at `@main` (not `@latest`).** `pipeline.yml`
   calls `Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main` then
   `container_pipeline.yml@main`; `pages.yml` calls `pages_pipeline.yml@main`. The
   Docker build-cache configuration (registry cache, `type=registry` — the org-wide
   convention from pipelines PR#1 that replaced expiring `type=gha` SAS tokens) lives
   **inside the reusable `container_pipeline.yml`**, not in per-repo workflows — never
   inline cache config in a connector repo. The CI image name is
   `${DOCKER_USERNAME}/${repo-name}`.

### Step 3: api-client [depends_on: scaffold-tree]

Read the `api-client-builder` skill and follow its instructions to:
1. Populate `{pkg_dir}/api/` sub-package:
   - `{pkg_dir}/api/api_client_base.py` — The HTTP/REST client base wrapper.
   - `{pkg_dir}/api/api_client_{domain}.py` — Domain-specific subclasses with API endpoint methods.
   - `{pkg_dir}/api/__init__.py` — Expose base and domain clients.
2. Keep `{pkg_dir}/api_client.py` — **Facade file** that re-exports from `api/` for backward compatibility.
3. Populate `{pkg_dir}/{short}_input_models.py` and `{pkg_dir}/{short}_response_models.py` —
   Pydantic input/response models (golden convention: two files named after the package,
   e.g. `gitlab_input_models.py` / `gitlab_response_models.py` — not a single `models.py`).
4. Update `{pkg_dir}/auth.py` — Configure authentication using **standard env var names**:
   - `{SERVICE}_URL` — Service endpoint (NOT `_BASE_URL` or `_INSTANCE`)
   - `{SERVICE}_TOKEN` — API token (NOT `_API_KEY`)
   - `{SERVICE}_SSL_VERIFY` — TLS verification (NOT `_VERIFY` or `_AGENT_VERIFY`)
   - `{SERVICE}_USERNAME` / `{SERVICE}_PASSWORD` — For basic auth

### Step 4: mcp-server [depends_on: scaffold-tree]

Read the `mcp-builder` skill and follow its instructions to:
1. Implement modular tool registrations inside `{pkg_dir}/mcp/` sub-package:
   - `{pkg_dir}/mcp/mcp_{domain}.py` — Houses dynamic action-routed tools per domain tag.
   - `{pkg_dir}/mcp/__init__.py` — Expose `register_{domain}_tools` functions.
2. Implement `{pkg_dir}/mcp_server.py` as the entrypoint:
   - Import `register_*_tools` from `{pkg_dir}/mcp/`
   - Gate each domain with env var toggles: `DEFAULT_{DOMAIN}TOOL` (env `{DOMAIN}TOOL`);
     mirror every toggle in `.env.example` and the root `mcp_config.json`.
   - Add CONCEPT ID to tool descriptions (e.g., `CONCEPT:{PREFIX}-001`)
3. **Tag Rules**: All MCP tool tags MUST be strictly lowercase with hyphens (e.g. `tag="user-management"`). No camelCase or underscores.
4. **Action-Routed Dynamic Generation**: ALL new agents use dynamic runtime generation. No monolithic static `@mcp.tool` files.
5. **Field Optimization**: All parameters use `pydantic.Field(default=..., description=...)`. No positional args in Field().

### Step 5: agent-server [depends_on: scaffold-tree]

Read the `agent-builder` skill and follow its instructions to:
1. Configure `{pkg_dir}/agent_server.py` with proper identity loading
   (`initialize_workspace()` + `load_identity()`), lazy `agent_utilities` imports,
   `warnings.filterwarnings`, and startup telemetry to `sys.stderr` (the pre-commit
   `check-agent-standards` hook enforces the latter two).
2. Keep `{pkg_dir}/main_agent.json` — the main-agent prompt definition.
3. Create `{pkg_dir}/__main__.py` invoking `agent_server()`.
4. Update `a2a.json` with the agent's real capabilities.

### Step 6: docs-generation [depends_on: api-client, mcp-server, agent-server]

Generate the full 7-page docs site (`mkdocs.yml` nav order is canonical):
`index.md` (hub w/ badges + grid cards), `overview.md`, `installation.md`,
`deployment.md`, `usage.md`, `platform.md` (backing-platform Docker recipe),
`concepts.md`.

#### docs/concepts.md (REQUIRED)
Every project must have a CONCEPT ID registry:
```markdown
# Concept Registry — {package-name}

> **Prefix**: `CONCEPT:{PREFIX}-*`
> **Bridge**: `CONCEPT:ECO-4.0` (Unified Toolkit Ingestion)

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:{PREFIX}-001` | {Domain 1} | MCP tool domain `{tag}` |
| `CONCEPT:{PREFIX}-002` | {Domain 2} | MCP tool domain `{tag}` |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |
```

Also keep `CHANGELOG.md` (Keep a Changelog) and the `AGENTS.md` + `CLAUDE.md` stub
pattern current: `CLAUDE.md` contains only the `@AGENTS.md` import; all guidance —
including the **Quality Bar** and **Git Worktrees** sections — lives in `AGENTS.md`.

### Step 7: verify-build [depends_on: docs-generation]

Validate build syntax and entry points:
- **Validate syntax**: Run syntax checking `python -c "import tomllib; ..."`
- **Lock**: `uv lock`
- **Test entry points**: `pip install -e . && {short}-mcp --help && python -m {pkg_dir} --help`

### Step 8: run-pre-commit [depends_on: verify-build]

Run all formatting and style hooks across the scaffold:
- **Run pre-commit**: `pre-commit run --all-files`

### Step 9: drift-check [depends_on: run-pre-commit]

Run a drift audit against the golden standard to confirm 100% compliance before
marking the package as complete. The full checklist is `PARITY_MANIFEST.md`; the
quick gate:

```bash
cd {project_dir} && echo "=== Drift Audit ===" \
  && for f in README.md CHANGELOG.md AGENTS.md CLAUDE.md LICENSE MANIFEST.in \
    pyproject.toml pytest.ini requirements.txt uv.lock mkdocs.yml \
    .pre-commit-config.yaml .bumpversion.cfg .gitignore .gitattributes \
    .dockerignore .codespellignore .vulture_ignore .env.example \
    a2a.json opencode.json mcp_config.json; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docs/index.md docs/overview.md docs/installation.md docs/deployment.md \
    docs/usage.md docs/platform.md docs/concepts.md; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docker/Dockerfile docker/debug.Dockerfile docker/agent.compose.yml \
    docker/mcp.compose.yml docker/starship.toml; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in .github/workflows/pipeline.yml .github/workflows/docs.yml \
    .github/workflows/pages.yml; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in scripts/security_sanitizer.py scripts/verify_api_integration.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in {pkg_dir}/__init__.py {pkg_dir}/__main__.py {pkg_dir}/mcp_server.py \
    {pkg_dir}/agent_server.py {pkg_dir}/api_client.py {pkg_dir}/auth.py \
    {pkg_dir}/mcp_config.json {pkg_dir}/main_agent.json; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && [ -d "{pkg_dir}/mcp" ] && echo "✅ mcp/ subdir" || echo "❌ mcp/ MISSING" \
  && [ -d "{pkg_dir}/api" ] && echo "✅ api/ subdir" || echo "❌ api/ MISSING" \
  && for f in tests/conftest.py tests/test_concept_parity.py \
    tests/test_init_dynamics.py tests/test_startup.py tests/test_auth.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && grep -q "ECO-4.0" docs/concepts.md && echo "✅ ECO-4.0 bridge" \
    || echo "❌ ECO-4.0 bridge MISSING" \
  && grep -q "pipelines/.github/workflows/python_pipeline.yml@main" \
    .github/workflows/pipeline.yml && echo "✅ pipeline @main" \
    || echo "❌ pipeline not pinned @main"
```

If ANY item shows ❌, fix it before completing the build. The `ecosystem_standardizer` workflow can also be run for a deeper audit with scoring.
```
Trigger: "run ecosystem standardizer" with scope={package-name}
```

### Step 10: remote-provisioning [depends_on: drift-check]

Create the package's remote homes using the fleet's own connectors (NOT manual
clicks). Both require credentials and are outward-facing — confirm with the user
once per session before the first creation call.

1. **GitHub repository** — via the **github-agent** MCP server tools (repo
   creation + settings; credentials from `agents/github-agent/.env`:
   `GITHUB_URL`/`GITHUB_TOKEN`). Repo name = the solidified package name.
   Immediately after creation, **ALWAYS enable GitHub Pages with the
   Actions build type** (the docs/pages workflows fail without it):
   `POST /repos/{owner}/{repo}/pages` with `{"build_type": "workflow"}`
   (201 = enabled, 409 = already enabled). Then apply the remaining standard
   settings (Actions enabled) — the github-project-provisioner skill covers
   defaults. Note the residual first-deploy race: even with Pages pre-enabled,
   the very first pages deploy may need a rerun-failed-jobs.
2. **DockerHub image repository** — via the **dockerhub-api** MCP server tools
   (`hub_repos` action `create`; credentials use the OFFICIAL hub-tool env
   names: `DOCKER_HUB_USER` / `DOCKER_HUB_TOKEN`). Image path =
   `{DOCKER_HUB_USER}/{package-name}`, matching the `image:` references in
   `docker/agent.compose.yml` + `docker/mcp.compose.yml` and the container
   pipeline's push target.
3. **Wire-up** — `git remote add origin <github-url>`; verify the
   `docker/*.compose.yml` image paths and workflow registry references match
   the created DockerHub repo; register the project in the workspace.yml set
   (root `/home/apps/workspace/workspace.yml` + the repository-manager and
   agent-utilities XDG-config copies — all three must stay in sync) so
   repository-manager validation tracks it.

Push only when the user asks (releases go through the phased auto_push flow).

> [!IMPORTANT]
> A new package is not complete until it passes the drift check with 0 missing items. This is a hard gate.

## Environment Variable Standard

All new agent packages MUST use these naming patterns:

| Pattern | Example | Notes |
|---------|---------|-------|
| `{SERVICE}_URL` | `PORTAINER_URL` | NOT `_BASE_URL` or `_INSTANCE` |
| `{SERVICE}_TOKEN` | `PORTAINER_TOKEN` | Prefer over `_API_KEY` |
| `{SERVICE}_SSL_VERIFY` | `PORTAINER_SSL_VERIFY` | NOT `_VERIFY` or `_AGENT_VERIFY` |
| `{SERVICE}_USERNAME` | `PORTAINER_USERNAME` | For basic auth |
| `{SERVICE}_PASSWORD` | `PORTAINER_PASSWORD` | For basic auth |

Preserve first-party env var names when they exist (e.g., `GITHUB_TOKEN`, `LANGFUSE_PUBLIC_KEY`).

## CONCEPT ID Prefix Registry

When assigning a prefix, check this registry to avoid collisions:

| Prefix | Project | | Prefix | Project |
|--------|---------|---|--------|---------|
| `ABOX` | archivebox-api | | `ARR` | arr-mcp |
| `ATL` | atlassian-agent | | `AU` | agent-utilities |
| `ANSIBLE` | ansible-tower-mcp | | `AUDIO` | audio-transcriber |
| `CLA` | clarity-api | | `CMGR` | container-manager-mcp |
| `DSCI` | data-science-mcp | | `EE` | emerald-exchange |
| `FAN` | fan-manager | | `GENIUS` | genius-agent |
| `GH` | github-agent | | `GL` | gitlab-api |
| `HASS` | home-assistant-agent | | `JELLYFIN` | jellyfin-mcp |
| `LF` | langfuse-agent | | `LIX` | leanix-agent |
| `LM` | listmonk-api | | `MEAL` | mealie-mcp |
| `MDLD` | media-downloader | | `MSFT` | microsoft-agent |
| `NC` | nextcloud-agent | | `OC` | owncast-agent |
| `PA` | postiz-agent | | `PLANE` | plane-agent |
| `PORT` | portainer-agent | | `QBT` | qbittorrent-agent |
| `RM` | repository-manager | | `ROM` | rom-manager |
| `SNOW` | servicenow-api | | `SRX` | searxng-mcp |
| `SX` | scholarx | | `SYS` | systems-manager |
| `STIRLINGPDF` | stirlingpdf-agent | | `TUI` | agent-terminal-ui |
| `TUN` | tunnel-manager | | `UKA` | uptime-kuma-agent |
| `VEC` | vector-mcp | | `WEBUI` | agent-webui |
| `WGER` | wger-agent | | | |
