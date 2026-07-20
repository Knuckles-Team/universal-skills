---
name: microstructure-trading-loop
skill_type: workflow
description: >-
  Orchestrates the KG-driven microstructure trading loop end-to-end: curate
  trading books/research into the knowledge graph, backtest microstructure
  signals and write priors back, seed Bayesian signal fusion from those priors,
  run paper-first trading decisions via the curated trading team, journal each
  decision, and evaluate (human-gated) stage graduation.
domain: finance-workflows
agent: quant_analyst
team_config:
  name: trading_paper_v1
  task_pattern: >-
    multi-asset paper-first trade research, validation, sizing and staged
    execution across equities, crypto, prediction markets, and derivatives
  execution_mode: parallel
  specialist_ids:
    - market-analyst
    - alpha-strategist
    - risk-manager
    - execution-specialist
    - attribution-analyst
  tool_assignments:
    market-analyst: [graph_search, document_process, emerald_market_data]
    alpha-strategist: [graph_query, ontology_query, emerald_signals, emerald_strategy]
    risk-manager: [graph_query, graph_analyze, emerald_risk]
    execution-specialist: [emerald_orders, emerald_market_making]
    attribution-analyst: [graph_write, emerald_portfolio]
tags: [microstructure, knowledge-graph, signal-fusion, paper-first, lifecycle]
concept: CONCEPT:EE-040
metadata:
  version: '1.2.1'
---

# Microstructure Trading Loop

**CONCEPT:EE-040**

Orchestrates the full KG-driven microstructure trading loop built on the
`feat/trading-agent-microstructure` work across emerald-exchange, agent-utilities,
epistemic-graph, and data-science-mcp. The loop curates trading knowledge into the
knowledge graph, turns backtested results into measured signal priors that drive
signal-fusion weights, runs **paper-first** decisions through the curated trading
team, and only ever *reports* graduation eligibility — promotion to live remains a
human action.

The two ingestion roots (`ingest-knowledge`, `research-goldenloop`) run in
parallel and converge at `register-substrate`; everything downstream is a linear
chain so each stage consumes the prior stage's KG state.

## Steps

### Step 0: ingest-knowledge
**Agent**: `market-analyst`
**Tools**: `graph_search, document_process`

Ingest trading books, papers, PDFs, and notes and ORGANISE them into the trading
knowledge taxonomy via `agent_utilities.knowledge_graph.distillation.trading_curator`
(`organize_trading_knowledge`): each extracted concept is classified into a
Strategy/Risk/Execution concept node with citations and confidence, and order-flow
chapters seed `MicrostructureSignal` nodes (`DERIVED_FROM`). Knowledge is organised,
not dumped.
Expected: `trading-knowledge-nodes`, `seeded-signal-stubs`

### Step 1: research-goldenloop
**Agent**: `market-analyst`
**Tools**: `graph_search`

Run the research golden-loop over the q-fin cluster (`research_pipeline`
RELEVANCE_TAXONOMY `trading` + `q-fin.*` categories): discover and score
microstructure / execution / risk papers, ingest the relevant ones, and route them
through the same `trading_curator` organise pass so papers and books land in one
typed taxonomy.
Expected: `ingested-research-concepts`

### Step 2: register-substrate [depends_on: Step 0, Step 1]
**Agent**: `alpha-strategist`
**Tools**: `ontology_query, graph_query`

Ensure the trading ontology (`ontology_trading.ttl`), the `MicrostructureSignal`
candidates, and the curated `teamcfg:trading_paper_v1` TeamConfig are registered in
the KG (`agent_utilities.graph.trading_team_seed.seed_trading_team`). This is the
substrate the rest of the loop reasons over.
Expected: `registered-signals`, `seeded-team-config`

### Step 3: backtest-signals [depends_on: Step 2]
**Agent**: `risk-manager`
**Tools**: `graph_analyze, graph_query`

Backtest each candidate microstructure signal via emerald `emerald_strategy`
(`backtest`) / data-science-mcp `quant_validation`, computing deflated Sharpe,
PBO, and hit-rate. Write the measured results back onto each `MicrostructureSignal`
node as priors (`FinanceEngineMixin.record_backtest_outcome`), discarding signals
with `pbo > 0.5` or `standalone_sharpe <= 0`.
Expected: `signal-priors-written`

### Step 4: seed-fusion [depends_on: Step 3]
**Agent**: `alpha-strategist`
**Tools**: `graph_query, emerald_signals`

Seed `BayesianSignalFusion` from the stored priors
(`seed_from_kg`: weight = directional_accuracy × standalone_sharpe) and fuse the
live signal directions through emerald `emerald_signals` (`fuse`). Require the
convergence gate to pass before any decision is emitted.
Expected: `fused-conviction`, `convergence-gate-result`

### Step 5: paper-decisions [depends_on: Step 4]
**Agent**: `execution-specialist`
**Tools**: `emerald_orders, emerald_market_making`

Compose/reuse the trading team and run paper-first decisions: size via Kelly
through the risk guards, route to the PAPER backend, and apply the queue-position /
toxicity / conviction gates. The staged-execution policy (`execution_policy.json`)
keeps this on paper; live submission is refused unless a human has promoted the
stage.
Expected: `paper-orders`, `quote-decisions`

### Step 6: journal-decisions [depends_on: Step 5]
**Agent**: `attribution-analyst`
**Tools**: `graph_write`

Write one `TradeJournalNode` per decision (instrument, stage, direction, size,
signals used, priors snapshot, rationale, regime) via `graph_write`, closing the
feedback loop so recurring profitable patterns can later be distilled into reusable
strategy concepts.
Expected: `trade-journal-entries`

### Step 7: evaluate-graduation [depends_on: Step 6]
**Agent**: `risk-manager`
**Tools**: `graph_query`

Run `RiskGuard.evaluate_graduation` against the journal + priors and REPORT whether
the current stage is eligible to advance (paper → advisory → bounded-autonomous).
This is eligibility-only: the workflow NEVER changes the stage. Promotion requires a
human running `approve_stage` with the `EMERALD_STAGE_APPROVAL_TOKEN`; the agent can
never self-escalate.
Expected: `graduation-eligibility-report`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — ingest-knowledge; Step 1 — research-goldenloop
- **After level 0:** Step 2 — register-substrate
- **After level 1:** Step 3 — backtest-signals
- **After level 2:** Step 4 — seed-fusion
- **After level 3:** Step 5 — paper-decisions
- **After level 4:** Step 6 — journal-decisions
- **After level 5:** Step 7 — evaluate-graduation

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
