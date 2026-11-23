# 2026-11-23 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Layer-depth pilot docs brought up to date after the normalised, capped five-depth run (documentation)

---

## 10:00 — Layer-depth pilot docs brought up to date after the normalised, capped five-depth run

Kind: documentation

- The pilot was rerun on node5 on 2026-11-20 (12:45–19:22) with the per-token normalisation,
  the cap and Gemma 3n stream 0: depths 25/50/67/75/100%, 21 models, Narratives and Nature
  Stories, 1352/1352 jobs per depth, no errors. Code files had been saved by 12:17, before the run.
- Check on the real checkpoints: the `*_embeddings.parquet` files of
  `results/tests/layer_depth_pilot_100/` are identical (max abs difference 0) to those of
  `results/language_models/<dataset>/embeddings/` for all 21 models and both datasets, quantised
  Gemma models included, so f = 1 reproduces the default embedding and the 100% summary tables
  differ from the main ones only by the cap.
- `docs/guides/running_and_troubleshooting.md`, section 1 "Layer-depth pilot": five depths
  including 100% (`--config relative_depth=<D/100>`, as in `run_snakemake_workflow.sh`), both
  datasets (copy loop over `narratives` and `nature_stories`), expected job count (1352), run time
  per depth (~1 h 20 min); the unchecked-quantisation warning replaced by the f = 1 check.
- `docs/reference/model_embeddings.md`: section 3 states the pilot scope (two datasets,
  25–100%) and the f = 1 check on the real checkpoints; section 5 gives the measured effect of the
  cap at the final layer (Narratives +0.01 5NN, +0.02 RSA on average; Nature Stories RSA +0.06 on
  average, up to +0.42, p < 0.05 in 14% → 32% of cases).
- Section times of `2026-11-20_new_feature_documentation.md` (both audiences) and of the matching
  `## Changes` entries corrected from 16:00/16:20 to 12:10/12:15, the file modification times of
  the code they describe.
- Pilot results recorded in `LLMmind/.claude/TODO/LLMmind_project.md` (S3 point 14); P6/S6
  closed there.

### Context

- Request: "the pilot run has ended, what are the results?", then "yes" to updating the TODO
  file, the changelogs and the layer-depth sections of the reference page and the running guide.
- Files changed: `docs/guides/running_and_troubleshooting.md`,
  `docs/reference/model_embeddings.md`, both `2026-11-20_new_feature_documentation.md`, this file
  and its user counterpart, `docs/AI_USAGE.md`.
- Verified: completion from the per-depth Snakemake logs; scores from the four summary tables of
  each depth directory (scratch script, not kept); embedding identity by comparing every pilot
  100% parquet file with the main one.
