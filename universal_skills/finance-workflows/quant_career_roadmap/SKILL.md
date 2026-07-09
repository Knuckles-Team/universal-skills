---
name: quant_career_roadmap
description: >-
  Zero-to-hired quant career roadmap as an executable DAG. Sequences the seven
  phases — math + Python foundations, finance fundamentals, first backtested
  strategy, ML for finance, the five-project GitHub portfolio, certifications,
  and the remote job search — with the month-overlap dependencies from the
  roadmap. Use to onboard and mentor a learner toward a quant role with no PhD.
domain: finance
agent: quant_career_mentor
team_config: quantitative_trading_team
tags: [quant, career, roadmap, finance, mentoring, workflow]
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---

# Quant Career Roadmap Workflow

The full path from zero to a (often remote) quant job — no PhD required. Consult
the `quant-career-docs` skill-graph for every formula, tool, and resource, and
route hands-on work to the role specialists (`quant_developer`, `quant_researcher`,
`quant_trader`, `risk_analyst`). The non-negotiable standard throughout is
**honest analysis**: always report Sharpe, max drawdown, and failure regimes.

## Steps

### Step 1: math-foundations
**Agent**: `quant_career_mentor`

Months 1–4. Build comfort with linear algebra, calculus, probability & statistics
(the core engine), and optimization via MIT OCW / Coursera "Mathematics for ML" /
3Blue1Brown. No university course required.
Expected: `math-readiness`

### Step 2: python-stack
**Agent**: `quant_developer`

Months 1–4. Learn the stack in order: NumPy, Pandas, Matplotlib/Plotly, SciPy,
scikit-learn, yfinance. First-day exercise: pull 5y of AAPL and plot a 30-day
rolling mean in a Jupyter notebook.
Expected: `python-fluency`

### Step 3: finance-fundamentals [depends_on: Step 1]
**Agent**: `quant_career_mentor`

Months 2–5. Markets 101 (price discovery, spread, order types), options & the
Greeks + Black-Scholes, bonds & duration, hedge-fund types, and the three
canonical edges (mean reversion, momentum, factor models).
Expected: `finance-vocabulary`

### Step 4: first-strategy-backtest [depends_on: Step 2, Step 3]
**Agent**: `quant_developer`

Months 3–6. Build a leak-free backtest in Backtrader/Zipline: SMA crossover first,
then pairs trading with cointegration. Compute Sharpe (>1.0 decent, <0.5 redo).
Audit for lookahead bias. Ship the first GitHub project.
Expected: `first-backtested-strategy`

### Step 5: ml-for-finance [depends_on: Step 4]
**Agent**: `quant_researcher`

Months 5–8. Regime detection with HMM, XGBoost/LightGBM on tabular features,
FinBERT sentiment. Predict direction not price; treat ML as feature discovery and
regime identification, not magic forecasting.
Expected: `ml-finance-capability`

### Step 6: portfolio-projects [depends_on: Step 4, Step 5]
**Agent**: `quant_career_mentor`

Months 6–12. Build at least 3 (ideally 5) of: pairs trading, Fama-French factor
model, GARCH volatility forecasting, FinBERT sentiment alpha, S&P-direction ML
classification. Enforce the GitHub rule: README (what + why), metrics
(Sharpe/max-drawdown/CAGR vs benchmark), clean code, honest "what didn't work".
Expected: `github-portfolio`

### Step 7: certifications [depends_on: Step 3]
**Agent**: `quant_career_mentor`

Optional, runs alongside the portfolio. CQF, CFA Level 1, QuantInsti EPAT, Andrew
Ng ML Specialization (do before financial ML), MIT OCW 18.S096. Pursue if budget
and goals warrant.
Expected: `credentials`

### Step 8: job-search [depends_on: Step 6]
**Agent**: `quant_career_mentor`

Months 7–12. Channels: LinkedIn, eFinancialCareers, QuantConnect, Numerai. Target
remote niches (crypto quant, fintech risk, AI+finance, consulting). Role-specific
interview prep: LeetCode/system-design (QD), brainteasers + Zetamac (QR/QT).
Expected: `offers-and-interview-readiness`

### Step 9: kg-persist [depends_on: Step 8]
**Agent**: `quant_career_mentor`
**Tools**: `graph_write`

Persist the learner's progress, completed projects, and metrics as typed nodes in
the Knowledge Graph, linked to the quant role and project entities.

## Output
- A phased, dependency-aware learning plan tracked in the KG
- A GitHub portfolio of 3–5 honestly-analyzed quant projects
- Interview-ready preparation and a realistic remote job-search plan

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — math-foundations; Step 2 — python-stack
- **After level 0:** Step 3 — finance-fundamentals
- **After level 1:** Step 4 — first-strategy-backtest; Step 7 — certifications
- **After level 2:** Step 5 — ml-for-finance
- **After level 3:** Step 6 — portfolio-projects
- **After level 4:** Step 8 — job-search
- **After level 5:** Step 9 — kg-persist

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
