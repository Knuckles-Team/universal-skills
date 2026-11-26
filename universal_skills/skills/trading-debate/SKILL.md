---
name: trading-debate
domain: finance
skill_type: skill
description: Run the TradingAgents swarm debate to vet financial hypotheses via Knowledge Graph orchestration.
metadata:
  version: '1.6.2'
---

# Trading Debate Skill

Use this skill to orchestrate multi-agent debate to peer-review and risk-veto trading hypotheses using `arbora`.

## Steps

1. Accept a `ResearchHypothesis` or `AlphaFactor` and write its identifier down. Verify with `graph_query` or `graph_search` that the node exists in the KG before debating it.
2. Start the debate with `graph_orchestrate(action="start_debate", task=<hypothesis>)`. Verify that the response lists agent personas such as Risk Manager and Macro Analyst with their positions.
3. Read each persona's response from the `start_debate` result and note any breached risk threshold. Verify that every persona returned a position, and rerun the debate if one is missing.
4. Submit a veto when a risk threshold is breached with `graph_orchestrate(action="submit_risk_veto", task=<hypothesis>)`. Verify that the response records the veto against the hypothesis.
5. Re-evaluate consensus, and on agreement link the hypothesis to a `TradingStrategy` node in the KG. Verify with `graph_query` that the hypothesis now has a link to a `TradingStrategy` node.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `start_debate` returns no personas | arbora is unreachable or the team is not configured | Check arbora reachability with `graph_search`, then restart the debate once it responds |
| Hypothesis node not found | The `ResearchHypothesis` was never ingested | Ingest or recreate it in the KG and use the new identifier |
| Consensus never reached after a veto | Risk Manager objection is unresolved | Revise the hypothesis to address the stated risk, and start a new debate on the revised text |
