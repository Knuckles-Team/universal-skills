---
name: train-model
skill_type: workflow
description: >-
  Agent-driven LLM training workflow: curate a corpus, train (fine-tune or pretrain from scratch), align, evaluate-gate, and register the checkpoint.
domain: machine-learning-workflows
agent: ml_orchestrator
team_config:
  name: model_training_team
  task_pattern: train, fine-tune, or pretrain a language model with agents
  execution_mode: sequential
  specialist_ids:
    - ml_orchestrator
    - data_curator
    - training_engineer
    - eval_judge
  tool_assignments:
    data_curator: [build_training_dataset, curate_corpus, dedup_corpus, decontaminate_corpus, prepare_pretrain_data, dataset_lineage, describe_dataset, split_dataset, compose_reward]
    training_engineer: [train_sft, train_reward, train_dpo, train_grpo, train_ppo, pretrain_model, train_tokenizer, merge_adapters_ties]
    eval_judge: [run_interpretability_suite, grade_response, evaluate_model, generate_interpretability_tests]
    ml_orchestrator: [graph_orchestrate]
tags: [ml, training, fine-tuning, pretraining, rlhf]
concept: CONCEPT:ML-007
metadata:
  version: '1.0.2'
---

# Train Model Workflow

**CONCEPT:ML-007**

Agent-driven end-to-end LLM training: curate a clean corpus, train (SFT/DPO/GRPO
fine-tuning, pretraining from random init, or the full **RLHF** stack — reward model
→ PPO), evaluate and gate at each stage, then register the final checkpoint so it
goes live. Backed by the `data-science-mcp` trainer + corpus engine and the
`model_training_team` personas.

## Steps

### Step 1: Pre Flight Config
**Agent**: `ml_orchestrator`
**Tools**: `graph_orchestrate`

Gather the objective from the user: fine-tune an existing base (SFT → DPO/GRPO) vs
pretrain a new small model from scratch; the base model id or architecture spec; the
corpus sources; the held-out eval sets; and the target serving role.
Expected: `pre_flight_config_artifacts`

### Step 2: Prepare Corpus [depends_on: pre_flight_config]
**Agent**: `data_curator`
**Tools**: `build_training_dataset, prepare_pretrain_data, describe_dataset`

Build the raw corpus: SFT records (and `{prompt, chosen, rejected}` preference pairs
for the reward model / DPO) from traces for fine-tuning; or, for pretraining, stream
text and `prepare_pretrain_data` it into a flat-token HDF5 file (CONCEPT:ML-010) the
trainer batches on the fly. Report record/token counts and a sample.
Expected: `prepare_corpus_artifacts`

### Step 3: Curate Corpus [depends_on: prepare_corpus]
**Agent**: `data_curator`
**Tools**: `curate_corpus, dedup_corpus`

Quality-filter (length/heuristics) and remove exact + near-duplicate records. Report
`n_in`/`n_out` and exact-vs-near removals.
Expected: `curate_corpus_artifacts`

### Step 4: Decontaminate Corpus [depends_on: curate_corpus]
**Agent**: `data_curator`
**Tools**: `decontaminate_corpus, dataset_lineage`

Drop any training record that leaks a held-out eval example, then emit a
`DatasetVersion` lineage node with the fingerprint. This must happen before training.
Expected: `decontaminate_corpus_artifacts`

### Step 5: Train Tokenizer [depends_on: decontaminate_corpus]
**Agent**: `training_engineer`
**Tools**: `train_tokenizer`

Pretrain-from-scratch path only: train a byte-level BPE tokenizer over the curated
corpus and save it. Skipped (no-op) when fine-tuning an existing base.
Expected: `train_tokenizer_artifacts`

### Step 6: Train Model [depends_on: decontaminate_corpus, train_tokenizer]
**Agent**: `training_engineer`
**Tools**: `train_sft, pretrain_model`

Plan, then (with a GPU) run the base training: `train_sft` for fine-tuning, or
`pretrain_model` (random init from the spec) for from-scratch. Choose precision,
scale-out, scheduler, and checkpointing; QLoRA first.
Expected: `train_model_artifacts`

### Step 7: Evaluate Base Training [depends_on: train_model]
**Agent**: `eval_judge`
**Tools**: `run_interpretability_suite, evaluate_model`

Score the checkpoint on the AHE-3.1 reliability suite (and benchmarks if available),
compare to the base, and return a gate decision: advance | repeat | abort.
Expected: `evaluate_base_training_artifacts`

### Step 8: Align Preferences [depends_on: evaluate_base_training]
**Agent**: `training_engineer`
**Tools**: `train_dpo, train_grpo`

Preference-align the SFT checkpoint without a reward model: `train_dpo` (direct
preference optimisation) or `train_grpo` (group-relative RL). The lightweight
alignment path; runs only when Step 7 gated `advance`. Skip when taking the full PPO
RLHF path (Steps 9–10) instead.
Expected: `align_preferences_artifacts`

### Step 9: Train Reward Model [depends_on: evaluate_base_training]
**Agent**: `training_engineer`
**Tools**: `train_reward`

Full-RLHF path: fit a Bradley-Terry reward model (CONCEPT:ML-008) on the
`{prompt, chosen, rejected}` preference corpus over the SFT backbone. Report the
held-out pairwise accuracy as a gate signal (expect ≳0.65 on real data). Skipped when
PPO uses a verifiable reward (e.g. GSM8K exact-match) or when only DPO/GRPO is used.
Expected: `train_reward_artifacts`

### Step 10: PPO Optimization [depends_on: train_reward_model]
**Agent**: `training_engineer`
**Tools**: `train_ppo`

RL-optimise the policy with PPO (CONCEPT:ML-009): rollouts scored by the Step-9 reward
model (`reward_source=reward_model`) or a verifier (`reward_source=verifier`), GAE
advantages + value head, clipped surrogate, KL-to-reference. Track mean reward and KL.
Expected: `ppo_optimization_artifacts`

### Step 11: Evaluate Alignment [depends_on: align_preferences, ppo_optimization]
**Agent**: `eval_judge`
**Tools**: `run_interpretability_suite, grade_response, evaluate_model`

Re-score the aligned/PPO checkpoint: AHE-3.1 reliability suite + (for reasoning) the
GSM8K exact-match verifier. Treat any safety/grounding regression as a hard fail and
return a gate decision.
Expected: `evaluate_alignment_artifacts`

### Step 12: Merge Adapters [depends_on: evaluate_alignment]
**Agent**: `training_engineer`
**Tools**: `merge_adapters_ties`

When multiple LoRA task vectors exist, TIES-merge them onto the base; otherwise pass
the single adapter through.
Expected: `merge_adapters_artifacts`

### Step 13: Final Evaluation [depends_on: merge_adapters]
**Agent**: `eval_judge`
**Tools**: `run_interpretability_suite, evaluate_model`

Final reliability + benchmark scoring of the merged checkpoint with the full delta
vs the base. Return the final gate decision.
Expected: `final_evaluation_artifacts`

### Step 14: Register Model [depends_on: final_evaluation]
**Agent**: `ml_orchestrator`
**Tools**: `graph_orchestrate`

Register the final checkpoint as a `ModelDefinition` bound to the target serving role
(the deploy seam — it goes live with no hot-path edit) and summarise the whole run,
linking corpus → tokenizer → pretrain/SFT → reward → PPO via the run lineage.
Expected: `register_model_artifacts`

## Output
- A trained, evaluated checkpoint registered to a serving role
- Per-stage artifacts: dataset version + fingerprint, training reports, gate decisions
- A run summary linking corpus provenance → training config → reward/PPO → eval scores
  → checkpoint (queryable via the `was_derived_from` lineage chain)

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pre Flight Config
- **After level 0:** Step 2 — Prepare Corpus
- **After level 1:** Step 3 — Curate Corpus
- **After level 2:** Step 4 — Decontaminate Corpus
- **After level 3:** Step 5 — Train Tokenizer
- **After level 4:** Step 6 — Train Model
- **After level 5:** Step 7 — Evaluate Base Training
- **After level 6:** Step 8 — Align Preferences; Step 9 — Train Reward Model
- **After level 7:** Step 10 — PPO Optimization
- **After level 8:** Step 11 — Evaluate Alignment
- **After level 9:** Step 12 — Merge Adapters
- **After level 10:** Step 13 — Final Evaluation
- **After level 11:** Step 14 — Register Model

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
