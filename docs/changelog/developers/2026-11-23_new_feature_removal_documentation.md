# 2026-11-23 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Layer-depth pilot docs brought up to date after the normalised, capped five-depth run (documentation)
- Layer-depth pilot run by its own Snakefile, with links instead of copies (new_feature, removal, documentation)

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

---

## 16:30 — Layer-depth pilot run by its own Snakefile, with links instead of copies

Kind: new_feature, removal, documentation

- New `workflow/layer_depth_pilot/Snakefile` (run with `snakemake -s
  workflow/layer_depth_pilot/Snakefile --cores 4 --resources gpu=1`): `configfile:
  "config/layer_depth_pilot.yaml"`; `LAYER_DEPTHS` (percent) from the new `relative_depths`
  key; `rule all` on the four summary tables of every depth; rule `run_layer_depth_pilot`
  (wildcard `depth`, `threads: 4`, `resources: gpu = 1`), whose shell block
  - links `results/tests/layer_depth_pilot_{depth}/{config,resources,workflow}` and
    `results/{mind,language_mind}/<dataset>` for every pilot dataset with `ln -sfnT` (relative
    targets; `-T` fails on a real directory);
  - runs `snakemake <targets> --directory … --configfile config/layer_depth_pilot.yaml
    --config relative_depth=<D/100> --use-conda --conda-prefix .snakemake/conda --cores 4
    --resources gpu=1 --allowed-rules <PILOT_RULES>`. `relative_depth` is formatted with `:g`
    (`1`, not `1.0`) so the `get_embeddings` shell text, which includes it, is the one the
    existing pilot embeddings were built with. `PILOT_RULES` holds the nine model-side rules, so
    brain, ISC, stimulus and download rules, which would write into the main results through
    the links, are never scheduled.
- `config/layer_depth_pilot.yaml`: new key `relative_depths: [0.25, 0.5, 0.67, 0.75, 1]`
  (ignored by the main Snakefile).
- `run_snakemake_workflow.sh`: the per-depth loop replaced by one call of the new Snakefile
  (`"$@"` passed on).
- Removed: the brain-result copies `results/tests/layer_depth_pilot_<D>/results/{mind,
  language_mind}/{narratives,nature_stories}` in the five pilot directories (2.4 GB → 652 MB for
  `results/tests/`), replaced by links to the main ones; the hand-made setup commands in the
  running guide.
- The 20 Nov pilot runs had rebuilt the Nature Stories `isc_dataframe.parquet` and ISC neighbour
  files in each copy (`create_isc_dataframe`: ISC `.npy` files of 2026-10-09 newer than the main
  `results/mind/nature_stories/isc_dataframe.parquet` of 2026-10-05); the rebuilt files are
  identical in content to the main ones (`DataFrame.equals`), so linking changes no result.
- Docs: `README.md` (layout, run commands), `docs/guides/running_and_troubleshooting.md`
  (section 1 "Layer-depth pilot" rewritten, `## Changes`), `docs/reference/model_embeddings.md`
  (section 3, `## Changes`).

### Context

- Request: "is it possible to include the pilot in the workflow? … a Snakemake file that runs
  the whole pilot (this workflow should create a symlink of all the folders required by the
  pilot …)", then TODO S7 approved ("approved, implement it right now (also, delete the
  copy-pasted file no longer needed by the pilot)") and "add the instructions to run the pilot to
  README.md and all the relevant documentation".
- Files changed: `workflow/layer_depth_pilot/Snakefile` (new), `config/layer_depth_pilot.yaml`,
  `run_snakemake_workflow.sh`, the three docs above, this file and its user counterpart,
  `docs/AI_USAGE.md`.
- Verified on the frontend (Snakemake 9.27.0): the outer dry run has nothing to do; with
  `--forcerun run_layer_depth_pilot -p` it prints the expected shell block (`relative_depth=1`
  at 100%); the inner command of every depth (25/50/67/75/100) with `--allowed-rules` has
  nothing to do after the links replaced the copies; with `--forcerun create_isc_dataframe`, the
  inner run schedules 2 `create_isc_dataframe` and 1270 dependent jobs without
  `--allowed-rules` and nothing with it. Not yet run for real on node5.
