---
name: freqtrade-executor
domain: finance
skill_type: skill
description: Execute paper-trading algorithms via freqtrader.
metadata:
  version: '1.0.2'
---

# Freqtrade Executor Skill

Use this skill to convert a vetted trading hypothesis into an executable crypto trading bot via `freqtrade`.

## Workflow
1. Read the `ConsensusRound` from the Knowledge Graph.
2. Formulate `freqtrade` strategy code from the consensus.
3. Validate against the Safety framework (Must be Paper-Trading Only).
4. Use `graph_orchestrate` (`execute_freqtrade`) to deploy the signal generation locally.
