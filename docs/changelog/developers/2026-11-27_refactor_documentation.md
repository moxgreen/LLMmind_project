# 2026-11-27 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Layer-depth pilot results with OpenLLaMA recorded; rerun recipe for adding models documented (documentation)
- The layer-depth pilot and the other additional tests are all called tests in the documentation (documentation)
- "pilot" removed from the layer-depth test's files, rule, variables and result directories (refactor, documentation)

---

## 11:45 — Layer-depth pilot results with OpenLLaMA

Kind: documentation

- Run (developer, node5, 2026-11-27 11:04–11:21): each depth's inner workflow run directly with
  `--rerun-triggers mtime input`, 196 jobs per depth (OpenLLaMA embeddings and downstream, four
  aggregations), 3–6 min per depth. The 21 BLOOMZ and Gemma embeddings of 2026-11-23 were not
  recomputed; all four summary tables of every depth now hold 24 models.
- `docs/reference/model_embeddings.md`, section 3: 24 models; OpenLLaMA blocks (26/32/40,
  *k* at 75% = 20/24/30); final-layer reference is the main `results/tsv_summaries/` as they are
  (same 24 models, same Benjamini-Hochberg families, so no re-correction); depth table with an
  OpenLLaMA row (0.495 / 0.504 / 0.500 / 0.492 / 0.477) and a "Last layer" column; Narratives local
  p < 0.05 now 93 / 95 / 92 / 85% against 73%; pooled size trend over 24 models 9 of 12 conditions,
  ρ −0.42 to −0.75; OpenLLaMA within-family ρ; Nature Stories RSA p < 0.05 19 / 10 / 12 / 19% against
  30%. The final norm is described as any `ln_f` or `norm` layer.
- `docs/guides/additional_tests.md`, section 1: 24 models, 1540 jobs per depth, about 5 h 30 min;
  new paragraph "Adding models without recomputing the others" with the inner-run loop.
- `README.md`: run time of the additional tests (about 5 h 30 min).

### Context

- Request: "the run ended, and the latest test result have been computed".
- Files changed: the three documentation files above, `docs/AI_USAGE.md`.
- Verification: a scratchpad script (summary tables only; `benjamini_hochberg()` from
  `workflow/libraries/compute_statistics.py`; enrichment = `observed_average_alignment_score` /
  `empirical_null_mean_alignment_score`) first reproduced every number of the previous 21-model
  documentation and manuscript table exactly (counts, medians, family means, shares of p < 0.05,
  pooled size trend), then computed the 24-model values. The last-layer column for 24 models
  equals the main tables (for example Narratives local Spearman 23/24, Nature Stories RSA
  Pearson 1/24).

---

## 13:40 — Additional tests named as tests

Kind: documentation

- Prose only; file, rule, config and results-directory names are unchanged (`layer_depth_pilot`,
  `run_layer_depth_pilot`, `config/layer_depth_pilot.yaml`, `results/tests/layer_depth_pilot_<D>/`,
  `narratives_dependencies`, `duration_length_controls`, `similarity_type_check`, `image_overlap`,
  `regional_crossover`). `## Changes` sections and changelogs keep their original wording.
- "Layer-depth pilot" becomes "layer-depth test" in `README.md`, `docs/guides/additional_tests.md`,
  `docs/guides/running_and_troubleshooting.md`, `docs/reference/model_embeddings.md` and
  `docs/reference/study_overview.md` (a script replaced the standalone word "pilot" outside fenced
  code blocks, so `layer_depth_pilot` identifiers stayed; every replaced line was reviewed).
- The other tests: "Narratives dependency test", "duration and length test", "similarity-type
  test", "image overlap test", "regional crossover test" (guide table, section headings and
  introduction; `README.md` index); `docs/reference/statistics.md`, section 8 is "Robustness tests
  of the whole-cortex results"; titles or mentions updated in `regional_crossover.md`,
  `fmri_preprocessing.md` and `study_overview.md`.
- `docs/reference/study_overview.md` also lost a stale description: the layer-depth test is now
  given as 24 language models at four intermediate depths compared with the main analysis' last
  layer (was 21 models at five depths), and OpenLLaMA joins the families that align better at
  intermediate depths.

### Context

- Request: "I would not name the layer depth test 'pilot' anymore: this is a test. update the
  project documentation accordingly", then "the change about the layer depth test should apply to
  every other test"; naming "<topic> test" chosen by the developer.
- Files changed: the seven documentation files above, `docs/AI_USAGE.md`.
- Verification: each exact replacement was required to match once (the script stops otherwise);
  `grep -i pilot` on the bodies of the living documents now finds only identifiers.

---

## 15:25 — "pilot" removed from the layer-depth test's code and outputs

Kind: refactor, documentation

- `workflow/additional_tests/layer_depth_pilot/` → `workflow/additional_tests/layer_depth/`;
  `config/layer_depth_pilot.yaml` → `config/layer_depth.yaml` (both `mv`, contents otherwise kept).
- In the test's Snakefile: `configfile:` and the inner `--configfile` point to
  `config/layer_depth.yaml`; `PILOT_DIR` → `DEPTH_DIR` (`results/tests/layer_depth_{depth}`),
  `PILOT_TARGETS` → `DEPTH_TARGETS`, `PILOT_RULES` → `ALLOWED_RULES`; rule
  `run_layer_depth_pilot` → `run_layer_depth`; `params.pilot_dir` → `params.depth_dir`; comments.
- Results moved with `mv`: `results/tests/layer_depth_pilot_{25,50,67,75}` →
  `results/tests/layer_depth_{25,50,67,75}`. The links inside each directory are relative and at the
  same depth, and each inner run's `.snakemake/` moved with its directory, so nothing is recomputed.
- Comments only: `config/config.yaml` (`relative_depth` is set per depth by the test's Snakefile;
  the old comment still said "set to 0.75 by config/layer_depth_pilot.yaml"), `workflow/Snakefile`
  (`model_subset` overlay example) and `workflow/llm_nearest_neighbours/Snakefile`
  (`relative_depth_arg`, a comment under `params:`, not part of any value Snakemake tracks).
- Documentation: paths, the rule name and the rerun loop in `README.md`,
  `docs/guides/additional_tests.md` and `docs/reference/model_embeddings.md` (bodies only; `## Changes`
  sections and older changelogs keep the old names); `docs/guides/running_and_troubleshooting.md`
  lists `results/tests/layer_depth_pilot_<D>/` under leftover outputs.

### Context

- Request: "change pilot also in the code, were needed"; the developer approved the rename and asked
  to proceed although TODO S9 and S10 are not yet approved.
- Files changed: `workflow/additional_tests/layer_depth/Snakefile`, `config/layer_depth.yaml`,
  `config/config.yaml`, `workflow/Snakefile`, `workflow/llm_nearest_neighbours/Snakefile`, the four
  documentation files above, `docs/AI_USAGE.md`.
- Verification: `grep -i pilot` finds nothing in the code; a dry run of the test's Snakefile reports
  "Nothing to be done"; the links in `results/tests/layer_depth_25/` resolve; the documented inner
  loop (`--rerun-triggers mtime input --allowed-rules ...`) dry-runs to "Nothing to be done" at all
  four depths, and so does the main workflow with `--rerun-triggers mtime input`.

