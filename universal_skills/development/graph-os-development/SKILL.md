---
name: graph-os-development
domain: development
skill_type: skill
description: >-
  Develop inside the graph-os repository — the served GraphOS runtime (MCP/REST
  composition, the multiplexer and MCP fleet, gateway, control plane, WebUI
  hosting, A2A, browser control, deployment operations). Load BEFORE changing
  graph_os/ code, its entrypoints, fleet catalog handling or deployment
  commands. Use when the agent must build, fix or review graph-os code.
  Covers the package map, what must NOT live here, the sibling
  development bindings, test and gate commands, generated artifacts, and the
  traps specific to this repo. Shared lane, build, gate and landing rules are in
  graphos-ecosystem-development — load it first. Not for engine (Rust) work or
  connector authoring.
license: MIT
tags: [graph-os, graphos, mcp, fleet, gateway, runtime, development]
metadata:
  version: '1.3.1'
  author: Genius
---
# graph-os development

graph-os is the deployable composition layer: it authenticates, composes, routes,
supervises and projects. **Load `graphos-ecosystem-development` first** — isolation,
staging, `--no-verify` lane commits, build hosts, gate caps, landing and decisions are
defined there and are not repeated here.

## What lives here — and what must not

| Package | Owns |
|---|---|
| `graph_os.mcp_server` | MCP/REST composition, the serving lifecycle, shared action routing; entrypoint `graph_os.mcp_server.server:mcp_server` |
| `graph_os.fleet` | MCP child lifecycle, catalog discovery, OAuth admission, health, per-session tool loading |
| `graph_os.gateway` | REST routes, dashboard aggregation, widget projection, the host daemon |
| `graph_os.control_plane` | fleet reconciliation, action-policy enforcement |
| `graph_os.webui_host` | the WebUI co-service lifecycle |
| `graph_os.a2a` | Agent Card and unary A2A projection |
| `graph_os.browser_control` | governed browser catalog, lease, dispatch, outcome |
| `graph_os.deployment` | configuration, doctor, canaries, environment plans, production ops |

Not here: durable graph state and every RDF/OWL/SHACL semantic (EG — do not add `.ttl`
or shapes; the fleet catalog authority is EG), agent decisions and workflows (AU),
vendor clients and source effects (SDK + connectors), browser presentation (WebUI repo).
Capabilities moving IN from AU (messaging daemon and channel adapters, gateway,
deployment) land here as the single implementation — delete the AU copy in the same
cutover, never keep both.

## Rules specific to this repo

- **One event loop, one multiplexer.** The serving lifecycle owns one FastMCP loop and one
  multiplexer instance. Co-services submit work to that loop; never construct a second
  multiplexer or block another loop on `Future.result()`.
- **MCP and REST share one application service and one authorization decision.** Change
  and test both surfaces together.
- **Fail closed.** A capability waiting on another repo's public contract stays marked
  unavailable in `docs/status.md`; no alias, static fallback or fabricated receipt.
- **`stdio` stdout is protocol output** — diagnostics go to logging/stderr (`stdout-writes`
  gate).
- **Settings through the shared XDG configuration model**; a new environment variable only
  when configuration cannot express it (`env-sprawl` gate).
- **Service identity scopes are exact** (e.g. `capacity:throttle`, `capacity:admin`); never
  wildcard scopes, never `kg:admin`. Probing a change to sign-in or admission means probing
  the browser path, not only a service token.

## Commands

Python-only repository — no cargo. Sibling repos are bound as editable paths through
`.uv-workspace-siblings/` (AU, SDK, WebUI); point those links at the worktrees you mean to
test against and print the resolved paths before trusting a result.

```bash
uv sync --extra test
uv run pytest tests/<the files you touched> -x -n 2   # targeted, on the dev host
uv run ruff check <changed files> && uv run ruff format --check <changed files>
uv run mypy <changed files>
```

Heavier runs go through `py-remote-run <host> <lane> <worktree> -- <command>`. The full
hook suite (`complexity-staged`, `kiss-staged`, `dupehound-changed`, `jscpd-differential`,
`public-surface`, `tracked-privacy`, `supply-chain`, `ci-gate-replica`, `pytest`, …) is the
orchestrator's landing gate — design to it, do not run `--all-files` in a lane.

## Generated and derived artifacts

- `uv.lock` — regenerate once after every `pyproject.toml` edit in the change has frozen.
- Generated manifests and fleet registries — regenerate from source, never hand-edit.
- `docs/` is the public MkDocs site: `mkdocs build --strict`; keep `README.md` and
  `AGENTS.md` inside the public-surface contract (required headings, ≤240 lines, no
  absolute paths, no history language).

## Traps seen here

- A test that constructs the composition with fakes is not wiring evidence — trace a real
  entrypoint through composition to the owning service.
- Model-treated-as-dict: EG/SDK typed results are pydantic models, not dicts; `.get()` on
  one fails only at runtime.
- The editable sibling links resolve to whatever checkout they point at; a green run
  against canonical `main` says nothing about your lane's AU/SDK branch.
- Deploy: the WebUI image build is not a code deploy; graph-os runs the engine as an
  in-pod child, so an engine change is an image change plus a digest-pinned rollout.

## How to apply

1. Load `graphos-ecosystem-development` and confirm the change belongs in graph-os (above).
2. Find the public entrypoint and the single owning implementation before editing.
3. Implement once; wire MCP and REST to the same service; keep failures closed.
4. Run the targeted checks above and a live-path test through the real entrypoint.
5. Update `docs/status.md` / docs honestly, commit an explicit allowlist with
   `--no-verify`, and checkpoint STATE.md.

Execution: run directly, or delegate through graph-os `graph_orchestrate` with the same
rules. Use an economy model for inventory and mechanical edits.
