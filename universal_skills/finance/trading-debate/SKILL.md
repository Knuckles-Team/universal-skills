---
name: trading-debate
description: Run the TradingAgents swarm debate to vet financial hypotheses via Knowledge Graph orchestration.
---

# Trading Debate Skill

Use this skill to orchestrate multi-agent debate to peer-review and risk-veto trading hypotheses using `graph-os`.

## Workflow
1. Accept a `ResearchHypothesis` or `AlphaFactor`.
2. Trigger `graph_orchestrate` with `start_debate`.
3. Read the responses from different agent personas (e.g. Risk Manager, Macro Analyst).
4. If risk threshold is breached, submit `submit_risk_veto` via `graph_orchestrate`.
5. Re-evaluate consensus. If consensus is reached, link hypothesis to `TradingStrategy` in KG.
