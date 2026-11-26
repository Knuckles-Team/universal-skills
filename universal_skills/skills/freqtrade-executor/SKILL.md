---
name: freqtrade-executor
domain: finance
skill_type: skill
description: Execute paper-trading algorithms via freqtrader.
metadata:
  version: '1.6.2'
---

# Freqtrade Executor Skill

Use this skill to convert a vetted trading hypothesis into an executable crypto trading bot via `freqtrade`.

## Workflow
1. Read the `ConsensusRound` from the Knowledge Graph.
2. Formulate `freqtrade` strategy code from the consensus.
3. Validate against the Safety framework (Must be Paper-Trading Only).
4. Use `graph_orchestrate` (`execute_freqtrade`) to deploy the signal generation locally.

## Steps

1. Read the `ConsensusRound` from the Knowledge Graph with `graph_query` for the round id. Verify that the result returns the consensus fields (signal, pair, timeframe) and is not empty.
2. Draft the `freqtrade` strategy from the consensus and save it as `user_data/strategies/<Name>.py`. Verify that `freqtrade list-strategies --userdir user_data` lists `<Name>` without errors.
3. Validate the Safety framework constraint by checking `grep -n '"dry_run"' user_data/config.json`. Verify that the value is `true` and refuse to continue otherwise.
4. Deploy with `graph_orchestrate` using `execute_freqtrade`. Verify that the run status reports success and that the bot log shows dry-run mode.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `ConsensusRound` query returns nothing | Wrong round id or round not yet ingested | Run `graph_search` for recent `ConsensusRound` nodes, pick the correct id and rerun step 1. |
| `list-strategies` reports an import error | Generated strategy has a syntax error or missing indicator import | Open the traceback, fix the named line in the strategy file and rerun `freqtrade list-strategies`. |
| `dry_run` is `false` | Config is set for live trading | Set `"dry_run": true` in the config, and do not deploy until step 3 passes. |
| `execute_freqtrade` fails | Local freqtrade runtime unreachable | Read the `graph_orchestrate` run trace for the failing call, restore the runtime, and redeploy. |
