---
name: train_model
description: >-
  Agent-driven LLM training workflow: curate a corpus, train (fine-tune or pretrain from scratch), align, evaluate-gate, and register the checkpoint.
domain: ml
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
    data_curator: [build_training_dataset, curate_corpus, dedup_corpus, decontaminate_corpus, dataset_lineage, describe_dataset, split_dataset, compose_reward]
    training_engineer: [train_sft, train_dpo, train_grpo, pretrain_model, train_tokenizer, merge_adapters_ties]
    eval_judge: [run_interpretability_suite, grade_response, evaluate_model, generate_interpretability_tests]
    ml_orchestrator: [graph_orchestrate]
tags: [ml, training, fine-tuning, pretraining]
concept: CONCEPT:ML-007
---

# Train Model Workflow

**CONCEPT:ML-007**

Agent-driven end-to-end LLM training: curate a clean corpus, train (SFT/DPO/GRPO
fine-tuning or pretraining from random init), evaluate and gate at each stage, then
register the final checkpoint so it goes live. Backed by the `data-science-mcp`
trainer + corpus engine and the `model_training_team` personas.

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
**Tools**: `build_training_dataset, describe_dataset`

Build the raw corpus: SFT/DPO/GRPO records from traces for fine-tuning, or streamed
text for pretraining. Report record counts and a sample.
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

Fine-tune path only: preference-align the SFT checkpoint (`train_dpo`) or RL-optimise
it (`train_grpo`). Runs only when Step 7 gated `advance`.
Expected: `align_preferences_artifacts`

### Step 9: Evaluate Alignment [depends_on: align_preferences]
**Agent**: `eval_judge`
**Tools**: `run_interpretability_suite, grade_response`

Re-score the aligned checkpoint; treat any safety/grounding regression as a hard
fail. Return a gate decision.
Expected: `evaluate_alignment_artifacts`

### Step 10: Merge Adapters [depends_on: evaluate_alignment]
**Agent**: `training_engineer`
**Tools**: `merge_adapters_ties`

When multiple LoRA task vectors exist, TIES-merge them onto the base; otherwise pass
the single adapter through.
Expected: `merge_adapters_artifacts`

### Step 11: Final Evaluation [depends_on: merge_adapters]
**Agent**: `eval_judge`
**Tools**: `run_interpretability_suite, evaluate_model`

Final reliability + benchmark scoring of the merged checkpoint with the full delta
vs the base. Return the final gate decision.
Expected: `final_evaluation_artifacts`

### Step 12: Register Model [depends_on: final_evaluation]
**Agent**: `ml_orchestrator`
**Tools**: `graph_orchestrate`

Register the final checkpoint as a `ModelDefinition` bound to the target serving role
(the deploy seam — it goes live with no hot-path edit) and summarise the whole run.
Expected: `register_model_artifacts`

## Output
- A trained, evaluated checkpoint registered to a serving role
- Per-stage artifacts: dataset version + fingerprint, training reports, gate decisions
- A run summary linking corpus provenance → training config → eval scores → checkpoint
