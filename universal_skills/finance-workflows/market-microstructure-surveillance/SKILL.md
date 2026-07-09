---
name: market-microstructure-surveillance
skill_type: workflow
description: >-
  Defensive market-surveillance pipeline: pull a trailing order-flow/book window
  for a symbol, compute Kyle insider/stealth-trading scores (informed-flow share,
  detection hazard, legal-risk) via the engine surveillance_risk kernel, register
  and backtest the signal so it self-weights, evaluate the adverse-selection
  quoting posture, and persist a SurveillanceSignal report into the knowledge
  graph. Detection + maker protection only — never trade concealment.
domain: finance-workflows
agent: quant_analyst
tags: [microstructure, surveillance, adverse-selection, knowledge-graph, defensive]
concept: CONCEPT:EE-042
requires: ['agent-utilities']
metadata:
  version: '1.2.0'
---

# Market Microstructure Surveillance

**CONCEPT:EE-042 / EE-043** — distils Qiao & Xia (2026), *"Insider and stealth
trading with dynamic legal risk"* (arXiv:2605.27684), a continuous-time Kyle-type
model where surveillance intensity rises with abnormal order flow.

A **defensive** pipeline that scores a symbol's order flow for informed/stealth
trading and protects a market maker from adverse selection. It computes the Kyle
surveillance scores (engine `surveillance_risk`, `CONCEPT:KG-2.20k`), turns the
detector into a self-weighting `MicrostructureSignal` (the EE-033 priors loop),
evaluates the legal-risk quoting posture (`CONCEPT:EE-043`), and writes the result
back into the knowledge graph as a `SurveillanceSignal` (`CONCEPT:AU-KG.ontology.kyle-insider-stealth-surveillance`).

This is **detection and maker-protection** — surfacing toxic/informed/stealth flow
and widening or pulling quotes against it. It is NOT a tool for concealing trades
or evading regulators, and it never places live orders (the controller is
decision-only, gated by `RiskGuard`).

The steps form a linear chain: each consumes the prior stage's output, so the
detector is registered before it is backtested and weighted before it gates.

## Steps

### Step 0: pull-order-flow
**Agent**: `quant_analyst`
**Tools**: `emerald_market_data`

Pull a trailing top-of-book + buy/sell-volume window for the target symbol via
`emerald_market_data` and shape it into the surveillance window
`{buy_vol, sell_vol, p_mean, signed_flow, price_changes, baseline_sigma}`
(`signed_flow = buy_vol − sell_vol` per bucket; `price_changes` from the
microprice/`p_mean` series). `baseline_sigma` is the expected noise-trader flow
scale; pass 0 to let the kernel use the sample std.
Expected: `surveillance-window`

### Step 1: compute-surveillance [depends_on: Step 0]
**Agent**: `quant_analyst`
**Tools**: `emerald_signals`

Call `emerald_signals` action `surveillance` (`CONCEPT:EE-042`) with the window.
It routes to the engine `surveillance_risk` kernel and returns
`kyle_lambda` (price impact), `informed_share` (VPIN α), `detection_hazard`,
`cumulative_suspicion`, `stealth_ratio`, and `legal_risk_score` ∈ [0,1]; it also
registers a discoverable `MicrostructureSignal` node so the fusion path can find
it. Flag the symbol when `legal_risk_score` or `informed_share` is elevated.
Expected: `surveillance-scores`, `registered-signal-id`

### Step 2: backtest-priors [depends_on: Step 1]
**Agent**: `quant_analyst`
**Tools**: `emerald_strategy`

Backtest the surveillance signal's directional returns via `emerald_strategy`
action `backtest` (deflated Sharpe + PBO + hit-rate) and write the measured priors
back onto the registered `MicrostructureSignal` (`CONCEPT:EE-033`). This closes the
self-weighting loop: `BayesianSignalFusion.seed_from_kg` then weights the detector
by `directional_accuracy × standalone_sharpe`. Discard signals with `pbo > 0.5`.
Expected: `signal-priors-written`

### Step 3: evaluate-posture [depends_on: Step 2]
**Agent**: `quant_analyst`
**Tools**: `emerald_market_making, emerald_risk`

Run `MarketMakingController.decide` over the live book: the Kyle legal-risk gate
(`CONCEPT:EE-043`) surfaces `legal_risk_score`/`informed_share` and withdraws
quotes when the score exceeds `MMConfig.legal_risk_max` (operator threshold, e.g.
0.85). Then call `RiskGuard.evaluate_graduation`, which blocks paper→advisory
promotion on `max_legal_risk`. Report the resulting posture (quote / widen /
withdraw) and graduation eligibility — REPORT only, never self-escalate the stage.
Expected: `quote-posture`, `graduation-eligibility`

### Step 4: persist-report [depends_on: Step 3]
**Agent**: `quant_analyst`
**Tools**: `graph_write`

Persist a `SurveillanceSignal` node (`CONCEPT:AU-KG.ontology.kyle-insider-stealth-surveillance`) carrying the scores plus a
`grounded_in` edge to the source paper (`Article` arxiv:2605.27684) and a
`relates_to` edge to the relevant ecosystem `Concept`, then emit a surveillance
report flagging toxic/stealth windows. The OWL bridge reasons over the new node
transitively (grounded_in / supports) so the finding participates in cross-domain
inference. Reuse the `kg-report-persister` atomic skill for the write.
Expected: `surveillance-signal-node`, `surveillance-report`

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — pull-order-flow
- **After level 0:** Step 1 — compute-surveillance
- **After level 1:** Step 2 — backtest-priors
- **After level 2:** Step 3 — evaluate-posture
- **After level 3:** Step 4 — persist-report

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
