---
name: skill-eval-author
description: >-
  Author an eval suite for a skill. Add a golden case with tool mocks, add real
  prompts from traces, add author-judged cases, calibrate the judge, run the
  suite and read the band. Use when a skill has no evals, when a skill changed,
  or when an ablation result needs a reading.
license: MIT
metadata:
  version: '1.7.0'
  spec_digest: '0266e1fcf421bc00883750874ebaea2ac422df24b83c7318f7c2734180d1ee3e'
  domain: development
  skill_type: skill
  tier: core
  tags: [skills, evals, calibration, ablation]
---

# Author a skill eval suite

The engine runs and scores the suite. This skill shows how to build one that the engine can trust.

<!-- spec:begin -->
## Goal

Build an eval suite for a skill with the right case mix, a calibrated judge and an ablation check.

## Steps

1. Add one golden case with tool mocks.
   - Run: `skills.eval.case.add`
   - Verify: The answer accepts the case and shows its expected digest.
2. Add real prompts from traces with the expected trajectory.
   - Run: `skills.eval.case.add`
   - Verify: Each case holds the ordered list of skills and tools that a good run uses.
3. Add author-judged cases last.
   - Run: `skills.eval.case.add`
   - Verify: The answer accepts each case and the suite lists the cases in this order.
4. Calibrate the judge against an annotated set.
   - Run: `skills.eval.calibrate`
   - Verify: The answer shows an agreement score above the engine minimum.
5. Run the suite and read the band.
   - Run: `skills.eval.run`
   - Verify: The report names the band and scores outcome and trajectory apart.

## Outputs

- A suite with golden cases, real-prompt cases and author-judged cases.
- The pass-rate band of the first run.

## Tool actions

Required:
- `skills.eval.case.add`
- `skills.eval.calibrate`
- `skills.eval.run`

Forbidden:
- `skills.tier.promote`

## Error recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 1 fails | The check did not hold: The answer accepts the case and shows its expected digest | Read the refusal code in the table below and apply its recovery. |
| Step 2 fails | The check did not hold: Each case holds the ordered list of skills and tools that a good run uses | Read the trace again and write the trajectory from the calls that it holds. |
| Step 3 fails | The check did not hold: The answer accepts each case and the suite lists the cases in this order | Calibrate the judge first when the answer is JUDGE_NOT_CALIBRATED. |
| Step 4 fails | The check did not hold: The answer shows an agreement score above the engine minimum | Add more annotated cases and calibrate again with the larger set. |
| Step 5 fails | The check did not hold: The report names the band and scores outcome and trajectory apart | Read the refusal code in the table below and apply its recovery. |
<!-- spec:end -->

## Reading the results

- A pass rate between 70 and 90 percent is healthy. A pass rate of 100 percent is suspicious: the cases are too easy.
- Outcome and trajectory are separate scores. A run can reach the right output by the wrong path.
- A judge needs a calibration run against an annotated set before its scores count.
- An ablation effect inside the noise band is no effect. Do not promote on it.

## Refusal codes

| Failure | Cause | Recovery |
| --- | --- | --- |
| `JUDGE_NOT_CALIBRATED` | The judge has too little agreement or too few cases. | Run `skills.eval.calibrate` with at least 50 annotated cases. |
| `EVAL_RUN_NOT_CLEAN_ROOM` | The run read a host path. | Remove the host path from the case and run again in the clean room. |
| `EVAL_CASE_INVALID` | A case lacks its expected digest, its trajectory or a known tool mock. | Add the missing field. Use only tools that the skill names. |
| `ABLATION_WITHIN_NOISE` | The delta sits inside the noise band. | Stop and report that the effect is no effect. |
| `ABLATION_NOISE_BAND_MISSING` | Too few identical runs set the band. | Run the same arm again until the engine minimum is met. |
| `COMPILE_MODEL_UNKNOWN` | The model ref is not in the model catalog. | Use a model ref from the catalog and compile again. |
