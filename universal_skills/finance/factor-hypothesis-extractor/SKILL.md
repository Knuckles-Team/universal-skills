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
  version: '1.2.1'
  author: Genius
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
