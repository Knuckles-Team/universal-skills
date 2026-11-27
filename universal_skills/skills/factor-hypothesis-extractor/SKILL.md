---
name: factor-hypothesis-extractor
domain: finance
skill_type: skill
description: Convert an audited quantitative-finance paper or evidence packet into
  explicit, testable factor hypotheses without sourcing data or running a backtest.
  Use when reviewed academic claims must be translated into signal definitions, timing
  assumptions, test parameters, and falsification criteria before market-data ingestion.
license: MIT
tags:
- finance
- research
- factors
- hypothesis
- backtesting
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Factor Hypothesis Extractor

Translate reviewed evidence into a test contract. Preserve the paper's stated
population, period, lag, construction, and limitations; do not turn an association
into a causal or investable claim.

## Required evidence

Use the citation-audited paper or evidence packet, stable claim/source identifiers,
the intended asset universe, and any user-supplied market, timing, or cost constraints.
If the source omits a necessary definition, mark it unresolved instead of choosing a
convenient convention.

## Output contract

For each distinct hypothesis, return:

- A unique hypothesis ID and the exact source claim IDs supporting it.
- Signal inputs, transformations, formula or pseudocode, direction, expected
  relationship, and economic rationale as stated by the source.
- Information timestamp, publication or availability lag, lookback, prediction
  horizon, rebalance frequency, and holding period.
- Eligible universe, exclusions, grouping or neutralization, missing-value policy,
  weighting assumptions, benchmark, and required transaction-cost model.
- Primary metric, robustness slices, null hypothesis, falsification threshold, and
  conditions under which the result should be rejected.
- Leakage, look-ahead, survivorship, selection, multiple-testing, capacity, and
  replication risks supported by evidence or clearly labeled as reviewer concerns.
- A readiness status of `READY`, `NEEDS_CLARIFICATION`, or `NOT_TESTABLE`, with every
  unresolved input listed.

Do not retrieve market data, implement the signal, run a backtest, rank securities,
recommend an investment, or place an order. The output is a research specification,
not evidence that the factor works outside the cited study.

## Steps

1. Collect the audited paper or evidence packet and list its claim identifiers with `grep -n "claim" <packet-file>`. Verify that every claim you intend to use has a stable claim or source ID in the output.
2. Extract each distinct hypothesis with the fields in the Output contract: signal inputs, formula, direction, timing, lag, horizon, universe and costs. Verify that each hypothesis has a unique ID and cites source claim IDs, for example `grep -c "hypothesis_id" <output-file>` equals the number of hypotheses.
3. Mark every missing definition as unresolved instead of choosing a convention. Verify that `grep -n "NEEDS_CLARIFICATION" <output-file>` lists each hypothesis with an open input and names that input.
4. Assign each hypothesis a status of `READY`, `NEEDS_CLARIFICATION` or `NOT_TESTABLE` and add falsification thresholds and leakage risks. Verify that `grep -Ec "READY|NEEDS_CLARIFICATION|NOT_TESTABLE" <output-file>` is at least the hypothesis count and that no data retrieval, backtest or trade recommendation appears in the output.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Hypothesis cannot cite a claim ID | The packet lacks stable identifiers | Return the packet to the audit step for citation IDs and set the hypothesis to `NEEDS_CLARIFICATION`. |
| Timing or lag is not stated in the source | The paper omits the information timestamp | List the missing field as unresolved and do not pick a default convention. |
| Output reads as an investable claim | Association was turned into causal language | Rewrite using the paper's stated population, period and limitations and remove any recommendation. |
| A request asks for a backtest or data pull | Out of scope for this skill | Decline that part and hand the `READY` specification to the data-ingestion and backtest skills. |
