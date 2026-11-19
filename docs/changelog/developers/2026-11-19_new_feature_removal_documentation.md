# 2026-11-19 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Layer-depth pilot extended to the 16 enabled Gemma models (new_feature, documentation)
- Gemma 3n left out of the layer-depth pilot (removal, documentation)

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

---

## 11:10 — Gemma 3n left out of the layer-depth pilot

Kind: removal, documentation

- `config/layer_depth_pilot.yaml`: `gemma3n_e2b` and `gemma3n_e4b` removed from `model_subset`
  (14 Gemma keys remain). Nothing else in the file changed.
- Reason: batch job 89502 (`logs/LLMmind_89502.log`) stopped at 25% depth after 32 of 516 steps.
  `get_embeddings` for `gemma3n_e4b` failed in `extract_embedding_from_output()` →
  `hidden_state_at_relative_depth()` → `pool_hidden_state()` with `ValueError: Expected a 2D or 3D
  hidden-state tensor, got shape (4, 1, 2048, 2048)`: Gemma 3n's decoder carries 4 AltUp streams,
  and `output.hidden_states[k]` keeps them as a leading dimension; only the final
  `last_hidden_state` is merged. `gemma3n_e2b` has the same structure. No workflow code changed;
  `get_embeddings.py` still cannot read Gemma 3n at an intermediate depth.
- Of the Gemma models, only `gemma4_e2b` at 25% was written before the failure; whether its block
  selection is right has not been checked.
- `docs/guides/running_and_troubleshooting.md` (section 1, and `## Changes`) and
  `docs/reference/model_embeddings.md` (section 3, and `## Changes`): 14 Gemma models instead of
  16, and why Gemma 3n is left out.

### Context

- Request: "only remove gemma3n_e2b and gemma3n_e4b from model_subset in
  config/layer_depth_pilot.yaml", after the failure of job 89502.
- Files changed: `config/layer_depth_pilot.yaml`, `docs/guides/running_and_troubleshooting.md`,
  `docs/reference/model_embeddings.md`, `docs/AI_USAGE.md` (dates, renamed changelog paths), this
  changelog and the user changelog (renamed to add the `removal` kind).
- Not verified by a dry run: the pilot was not dry-run after the change.
