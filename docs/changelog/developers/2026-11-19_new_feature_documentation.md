# 2026-11-19 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Layer-depth pilot extended to the 16 enabled Gemma models (new_feature, documentation)

---

## 10:00 — Layer-depth pilot extended to the 16 enabled Gemma models

Kind: new_feature, documentation

- `config/layer_depth_pilot.yaml`: `model_subset` now lists, after the five BLOOMZ keys, the 16
  Gemma keys that are not commented out in `config/config.yaml`, in the same order: `gemma_2b`,
  `gemma_7b`, `gemma2_2b`, `gemma2_9b`, `gemma2_27b`, `gemma3_270m`, `gemma3_1b`, `gemma3_4b`,
  `gemma3_12b`, `gemma3_27b`, `gemma3n_e2b`, `gemma3n_e4b`, `gemma4_e2b`, `gemma4_e4b`,
  `gemma4_12b`, `gemma4_31b`. `gemma4_26ba4b` stays out (disabled in the main config: it does
  not fit on node5's GPU). Header comment updated. No workflow code changed; `MODEL_KEYS` in
  `workflow/Snakefile` already reads `model_subset`.
- Per depth directory (`results/tests/layer_depth_pilot_<D>/`), only the Gemma jobs are new: 516
  jobs (`get_embeddings` ×16, `compute_llm_nearest_neighbours` ×16, alignment, relabelling,
  hypergeometric and empirical p-value and Spearman ×96 each, aggregations ×4). The BLOOMZ outputs
  are reused; the two aggregation rules rerun because their input set changed.
- Not yet tested: `hidden_state_at_relative_depth()` (`get_embeddings.py`) on quantised models
  (bitsandbytes 8/4 bit) and on Gemma 3n, whose decoder carries several AltUp streams, so its
  intermediate `hidden_states` may have an extra leading dimension.
- `docs/guides/running_and_troubleshooting.md`, section 1 "Layer-depth pilot": rewritten to the
  current layout (four depths, one directory per depth under `results/tests/`,
  `--config relative_depth=0.<D>`, the loop in `run_snakemake_workflow.sh`; the old
  `results/layer_depth_pilot/` instructions removed), model list and job breakdown updated,
  warning on quantised models and Gemma 3n added.
- `docs/reference/model_embeddings.md`, section 3: the pilot's models and depths updated.

### Context

- Request: "modify the config file for the layer change pilot to include all Gemma models"; then
  "add the non-commented out 16 Gemma models listed in the original config file to the BLOOMZ
  ones".
- Files changed: `config/layer_depth_pilot.yaml`, `docs/guides/running_and_troubleshooting.md`,
  `docs/reference/model_embeddings.md`, `docs/AI_USAGE.md`.
- Verified with a dry run on the frontend in `results/tests/layer_depth_pilot_75`
  (`--config relative_depth=0.75`, `-n --quiet rules`): 516 jobs, all for the Gemma models; no
  ISC, stimulus, excluded-stimuli or download job. The other three depth directories were not
  dry-run.
