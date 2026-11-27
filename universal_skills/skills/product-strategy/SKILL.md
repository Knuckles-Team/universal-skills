---
name: product-strategy
domain: product
skill_type: skill
description: >-
  Developing product vision, market positioning, and financial modeling for
  product initiatives. Use when performing PESTEL/SWOT analysis, calculating
  TAM/SAM/SOM, defining market positioning, or creating SaaS financial
  diagnostics.
license: MIT
tags: [strategy, market-analysis, positioning, financial-modeling, saas-metrics]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# Product Strategy & Market Analysis

Define the strategic direction and economic viability of product initiatives.

---

## 1. Strategic Frameworks

Use these frameworks to understand the external and internal landscape.

### PESTEL Analysis
Analyze Macro-environmental factors:
- **Political**: Regulations, trade policies.
- **Economic**: Interest rates, inflation, consumer spending.
- **Social**: Trends, demographics, cultural shifts.
- **Technological**: AI advancements, infrastructure.
- **Environmental**: Sustainability, climate impact.
- **Legal**: Labor laws, IP protection.

### SWOT Analysis
- **Strengths/Weaknesses**: Internal factors.
- **Opportunities/Threats**: External factors.

---

## 2. Market Sizing (TAM/SAM/SOM)

Quantify the opportunity to ensure the investment is justified.

- **TAM (Total Addressable Market)**: Total global demand for the product category.
- **SAM (Serviceable Addressable Market)**: The portion of TAM that your business model/technology can realistically serve.
- **SOM (Serviceable Obtainable Market)**: The portion of SAM you can realistically capture in the next 1–3 years.

---

## 3. Market Positioning

Define how your product sits in the mind of the customer relative to the competition.

**Positioning Statement Formula**:
"For [target audience] who [statement of need], [product name] is a [product category] that [compelling benefit]. Unlike [primary competitor], we [primary differentiation]."

---

## 4. SaaS Economics & Metrics

Understand the "Health" of a digital product.

### Growth Metrics:
- **MRR / ARR**: Monthly / Annual Recurring Revenue.
- **NRR**: Net Revenue Retention (% of revenue kept from existing customers).
- **LTV**: Lifetime Value of a customer.
- **CAC**: Cost to Acquire a Customer.

### Efficiency Metrics:
- **LTV/CAC Ratio**: Aim for >3.0 for a healthy business.
- **Payback Period**: Months required to recover CAC.
- **Rule of 40**: Growth Rate + Profit Margin should be >40%.

---

## Steps

1. Capture the product, market and time horizon. Verify with `grep -n "TAM" SKILL.md` that you will apply the sizing formulas from section 2.
2. Run PESTEL and SWOT from section 1 on the initiative and list entries under `PESTEL:` and `SWOT:` headings. Verify that each PESTEL factor and each SWOT quadrant has at least one entry.
3. Size TAM, SAM and SOM per section 2 as `TAM >= SAM >= SOM`. Verify that SOM is no larger than SAM and SAM no larger than TAM, and that every assumption has a cited source.
4. Write the positioning statement using the section 3 formula (`For [target audience] who ...`). Verify that all bracketed fields are filled in.
5. Compute the SaaS metrics in section 4 with `python3 -c "print(ltv/cac)"` on the real values. Verify that LTV/CAC and the Rule of 40 are reported with the inputs.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Market size unsupported | Top-down numbers without sources | Add a bottom-up cross-check and cite a source for each input |
| Positioning statement is generic | Competitor and differentiation unspecified | Name the primary competitor and one concrete differentiator, then rewrite |
| LTV/CAC below 3.0 | High acquisition cost or low retention | Report it as a risk and show a sensitivity table for CAC and churn |

## Best Practices

- **Validate Assumptions**: Market sizing is only as good as its underlying assumptions. Document your sources.
- **Competitor Obsession**: Don't just list features; understand the competitor's business model and "Gaps" in their strategy.
- **Focus on Differentiation**: Why would a customer switch from a "Good enough" existing solution to yours?
- **Link to Execution**: Strategy is useless without a roadmap that builds toward the vision.
