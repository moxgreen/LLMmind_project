# 2026-11-26 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Five one-off analyses turned into additional tests under `workflow/additional_tests/`; documentation updated with their numbers (new feature, documentation)
- Effect of the BOS token on the language-model embeddings measured; no pipeline change (documentation)
- Concept-level plot rules, scripts and folders renamed from "scatterplot" to "boxplot" (refactor, documentation)
- New rule `plot_alignment_enrichment_model_size`: enrichment against model size, with within-family Spearman's ρ (new feature, documentation)

---

## 12:00 — Five one-off analyses turned into additional tests

Kind: new feature, documentation

- **Layout** (TODO S8): one folder per test under `workflow/additional_tests/`, each with its own
  `Snakefile` and `scripts/`, settings in `config/<test>.yaml`, outputs in `results/tests/<test>/`;
  none is included in `workflow/Snakefile` or `rule all`. Shared definitions in
  `workflow/additional_tests/additional_tests.smk` (included after the `configfile:` lines):
  `shell.prefix` with `PYTHONPATH`, `TESTS_DIR`, `ENVIRONMENT` (the `llm_mind_alignment`
  environment file, same content, so Snakemake reuses the built environment
  `.snakemake/conda/273bf7076eaea539fd63764652c1c761_`), `SPEARMAN_SUMMARY`, `models_of()`,
  `LANGUAGE_MODELS`, `model_embeddings()`.
- **New library** `workflow/libraries/relabelled_rsa.py`, from the old scratchpad `common.py`:
  `similarity_matrix()`, `brain_matrix()`, `model_matrix()` (now `capped_embedding_matrix()`, as
  `compute_spearman_alignment_with_empirical_p_value.py` reads the models since 2026-11-20; the
  old scripts read uncapped embeddings), `unit_ranks()`, `to_square()`,
  `relabelled_coefficients()`, `draw_permutations()` (the pipeline's relabelling stream),
  `read_published_spearman()`, `require_published_coefficient()` (tolerance 10⁻⁵).
- **Tests**, each with one rule (two for the crossover):
  - `narratives_dependencies` (from `b2_dependencies.py`, `b2_influence.py`; overlay
    `config/narratives_dependencies.yaml`: `unit_blocks`, `unrelated_units`): restricted
    permutations, leave-out RSA (each unit, each block, both 2-unit blocks, one unit per block,
    without the within-block pairs), unit distinctness → `restricted_permutations.tsv`,
    `leave_out.tsv`, `unit_distinctness.tsv`. The two swapped blocks are the blocks of size 2.
  - `duration_length_controls` (from `b3_duration.py`; overlay `repetition_times`) →
    `stimuli.tsv`, `models.tsv`, `brain_duration.tsv`, `mean_isc_associations.tsv`.
  - `similarity_type_check` (from `i17_narratives.py`; overlay `subsample_draws`, `top_parcels`,
    `log_offset`; the subsample size is now the smallest story's subject count, 14, instead of a
    constant; *k* from `config["narratives"]["number_of_neighbours"]`): stops unless the published
    condition reproduces `observed_average_alignment_score` and `model_level_empirical_p_value`
    within 10⁻⁶ and the recomputed ISC matches the published ISC → `summary.tsv`,
    `isc_properties.tsv` (label IDs written 1-based).
  - `image_overlap` (from `i22_coco_overlap.py`; no overlay; paths derived from
    `nsd_data.dataset_dir` and the Caption Scene `stimuli_dir.vision`) → `image_overlap.tsv`.
  - `regional_crossover` (the collaborator's `test_caption_scene.py`, `test_narratives.py`; overlay
    `similarity_type`, `bootstrap`): rules `regional_crossover_caption_scene`,
    `regional_crossover_narratives`, target `all_regional_crossover`. Same steps and random streams
    (`default_rng(20261109).integers`, `RandomState(42).choice`); reuse
    `read_nearest_neighbours()` with `read_stored_number_of_neighbours()`,
    `compute_alignment_scores()` (set intersection, equal to the scripts' merge count; Caption
    Scene stops on duplicate rows to keep it so) and `model_family()` (same groups, labels are the
    key prefixes). Not carried over: the 3-vs-4 return values and the array shape printed as k →
    `regional_crossover_caption_scene.tsv`, `regional_crossover_caption_scene_families.tsv`,
    `regional_crossover_narratives.tsv`.
- **Results** (first run, 2026-11-26, on the main run of 2026-11-25): the RSA-based numbers differ
  from the one-off values because of the cap (published Narratives RSA 0.428 / 0.460 / 0.549, was
  0.395 / 0.469 / 0.550; Nature Stories 0.237 / 0.210 / 0.197, was 0.099 / 0.168 / 0.196). New
  facts: the two pairings of the swapped blocks differ for one model (Gemma 2 27B, cosine); swapped
  permutations reach the observed ρ for that model; without the 17 highest-ISC parcels cosine
  reaches 22/24 corrected models (was 11). The crossover cells moved in the fourth decimal
  (A 1.1453, B 1.0113, C 1.2078, D 1.0012). The image overlap is unchanged.
- **Documentation:** `docs/guides/additional_tests.md` (table of tests, loop that runs them all,
  rerun rules, sections 2–6); `docs/reference/statistics.md` section 8 (status, numbers, the
  similarity-type conclusion); `docs/reference/regional_crossover.md` (status, numbers, checks,
  Narratives interval −0.3022 instead of the unchecked −0.3211, language-region significance
  24 / 24 / 21, DINOv2 RSA range); `docs/reference/fmri_preprocessing.md` (overlap source);
  `docs/reference/study_overview.md` section 6 (reproduced by additional tests vs one-off);
  `README.md` (index, layout, run-all command, `results/tests/` output).
- TODO P8/S8 solved and removed; SUGGESTIONS I23, I24, I25 refreshed (numbers, test names).

### Context

- Request: "S8 approved, implement it, and update all the necessary documentation and README.md.
  also, at the end, paste the command line that runs all the tests".
- Files added: `workflow/libraries/relabelled_rsa.py`,
  `workflow/additional_tests/additional_tests.smk`, the `Snakefile` and scripts of
  `narratives_dependencies`, `duration_length_controls`, `similarity_type_check`, `image_overlap`,
  `regional_crossover`, and `config/{narratives_dependencies,duration_length_controls,similarity_type_check,regional_crossover}.yaml`.
  Files changed: the documentation pages above, `docs/AI_USAGE.md`.
- Verification: the main run of 2026-11-25 completed (35,874 of 35,874 jobs) before the tests
  were run. Every test ran through Snakemake on the frontend with exit 0 (8 min, 2 min, 1 min 21 s,
  4 s, 59 s) and passed its built-in checks against the published tables. The collaborator's two
  scripts, run unchanged from the scratchpad on the same outputs, print the same cells, family
  medians, values and 95% intervals as the test. The image overlap matches the documented counts.
  After line wrapping, the crossover, duration and similarity tests were force-rerun: outputs
  byte-identical. `snakemake -n` on all six test Snakefiles: "Nothing to be done".

---

## 14:45 — Effect of the BOS token measured

Kind: documentation

- One-off check of SUGGESTIONS I4 (IS4), run outside the repository; no code changed.
  - **BOS vector.** On node5, *c* = `last_hidden_state` of `[BOS]` alone was computed for every
    language model (`get_embeddings.load_model()` with the configured quantization).
  - **BOS-free embeddings from the stored files** (frontend). G = (F − w·c)/ρ, with
    w = Σ Lᵢ/(Lᵢ+1)/S and ρ = Σ Lᵢ²/(Lᵢ+1)/S over the chunks of `embed_long_text()`.
  - **OpenLLaMA 13B (8-bit, LLM.int8)** is the exception: position 0 differs from *c* by up to
    62%, so its embeddings were recomputed directly. `embed_long_text()` was run with
    `extract_embedding_from_output()` wrapped to mask position 0. Chunking was checked against
    the stored `n_tokens`/`n_chunks`.
  - **Downstream.** Neighbours from `compute_topk_on_concept_subset()`, relabelled null from
    `compute_relabelled_common_neighbours_for_all_k()` (*N* = 10,000, seed 37), observed counts
    from `compute_common_neighbours()`; whole cortex, every similarity type and *k*.
- **Result** (24 models):
  - neighbour overlap 89–100%, median at least 97%;
  - largest alignment change: 0.0012 on Caption Scene, 0.011 on Narratives, under 0.0001 on Nature
    Stories;
  - BH q < 0.05 counts identical in every (dataset, similarity, *k*);
  - uncorrected p < 0.05 on Caption Scene at *k* = 5: cosine 4 → 6, Spearman 9 → 11.
- **Conclusions do not move,** so no `[heavy]` pipeline change follows.
- **Documentation:**
  - `docs/reference/model_embeddings.md`: section 3 gains "Measured effect of the BOS token";
    section 6 drops "the BOS outlier was not measured".
  - `docs/reference/study_overview.md`: the BOS limitation gives the result.
- SUGGESTIONS I4/IS4 removed.

### Context

- Request: "proceed with I4"; then "submit a short sbatch job" for the three OpenLLaMA models.
  Slurm jobs 89521 and 89522: placeholder jobs on node5 for ssh access, cancelled after use.
- Files changed: `docs/reference/model_embeddings.md`, `docs/reference/study_overview.md`,
  `docs/AI_USAGE.md`.
- Verification:
  - On two captions per model, the recomputed vector reproduces the stored one within 10⁻⁷, and
    the correction matches the direct BOS-free mean within 0.6% (all except OpenLLaMA 13B).
  - The original variant reproduces `observed_average_alignment_score` and
    `model_level_empirical_p_value` of `all_model_brain_alignment_scores.tsv` (language rows)
    within 8·10⁻⁶ and 5·10⁻¹¹.

---

## 17:30 — Concept-level "scatterplots" renamed to boxplots

Kind: refactor, documentation

- Scripts renamed with `git mv`: `plot_concept_alignment_scatterplot.py` →
  `plot_concept_alignment_boxplot.py`, `plot_concept_alignment_enrichment_scatterplot.py` →
  `plot_concept_alignment_enrichment_boxplot.py` (content unchanged apart from the header date).
- Rules renamed in `workflow/visualisation/Snakefile`: `plot_concept_alignment_scatterplot` →
  `plot_concept_alignment_boxplot`, `plot_concept_alignment_enrichment_scatterplot` →
  `plot_concept_alignment_enrichment_boxplot`.
- Output folders renamed (`results/pictures/`): `concept_alignment_scatterplots{suffix}/` →
  `concept_alignment_boxplots{suffix}/`, `concept_alignment_enrichment_scatterplots{suffix}/` →
  `concept_alignment_enrichment_boxplots{suffix}/`, `concept_spearman_alignment_scatterplots{suffix}/`
  → `concept_spearman_alignment_boxplots{suffix}/` (the `concept_level_plot` output of
  `plot_spearman_alignment`). The input keys of `rule all` and `rule all_visualisation` are renamed
  to match (`concept_*_boxplots`).
- Snakemake does not know the new paths, so the next run redraws these plots (57 + 57 + 27 jobs,
  about 18 min) and the matching `plot_spearman_alignment` jobs; no data is recomputed. The old
  folders are listed under "Leftover outputs from older versions" in the running guide and can be
  deleted after that run.
- TODO P11/S11 removed.

### Context

- Request: TODO S11, approved on 2026-11-26, then "implement S11 and S12".
- Files changed: `workflow/Snakefile`, `workflow/visualisation/Snakefile`, the two renamed scripts,
  `README.md`, `docs/reference/statistics.md`, `docs/reference/clean_run_duration.md`,
  `docs/guides/running_and_troubleshooting.md`, `docs/AI_USAGE.md`.
- Verification: no `scatterplot` left in `workflow/`; `snakemake -n` (see the next entry).

---

## 17:30 — Model-size analysis of the enrichment

Kind: new feature, documentation

- New rule `plot_alignment_enrichment_model_size` in `workflow/visualisation/Snakefile`, one job,
  `visualisation_environment.yaml`. Input: `all_model_brain_alignment_scores.tsv` (whole cortex).
  Params: `model_parameters`, `plot_pattern` (a function, so Snakemake does not expand its
  placeholders). Outputs: one PNG per `HEATMAP_PAIRINGS` entry,
  `results/pictures/model_size_lineplots/dataset-{dataset}_{similarity_type}-alignment_enrichment_model_size_{k}NN.png`
  (24 plots), and `results/tsv_summaries/model_size_within_family_spearman.tsv`. Paths are defined
  once as `MODEL_SIZE_LINEPLOT`, `MODEL_SIZE_LINEPLOTS` and `MODEL_SIZE_SPEARMAN` at the top of
  `workflow/visualisation/Snakefile` and used in the rule, `rule all` and `rule all_visualisation`.
- New script `workflow/visualisation/scripts/plot_alignment_enrichment_model_size.py`:
  - `read_enrichments()`: pivots the summary table and computes the model-level enrichment as
    `observed_average_alignment_score / empirical_null_mean_alignment_score`, adds
    `parameters_millions` and `model_family()`; stops if a model has no parameter count.
  - `plot_configuration()`: log10 x-axis of parameters, symlog enrichment y-axis
    (`set_enrichment_y_scale()`, limits from matplotlib's autoscaling), one line per family in a
    fixed `tab20` colour (`FAMILY_COLOURMAP`, `FAMILY_COLOUR_ORDER`), `STIMULI_TYPE_MARKERS` for the
    stimulus type, every point annotated with its model key, null line at 1, legend outside on the
    right; `save_figure(..., model_figure = False)`.
  - `within_family_spearman()`: Spearman's ρ as the Pearson correlation of the ranks (pandas, no
    SciPy), only for families with at least `MINIMUM_FAMILY_SIZE` = 3 models; no p-values. The TSV
    has columns `dataset`, `stimuli_type`, `similarity_type`, `number_of_neighbours`, `family`,
    `number_of_models`, `spearman_rho`, written with `%.6g` (147 rows on the current tables).
- Replaces the one-off model-size permutation test (scratchpad `b1_scale.py`); the across-models
  test with BH q-values and the RSA outcome are dropped, as the developer decided.
- TODO P12/S12 rewritten: what is left is to run the rule and update the manuscript's "Model
  Size" text and Appendix A.

### Context

- Request: TODO S12, rewritten and approved by the developer on 2026-11-26, then "implement S11
  and S12".
- Files changed: `workflow/Snakefile`, `workflow/visualisation/Snakefile`, the new script,
  `README.md`, `docs/reference/statistics.md` (sections 7 and 8),
  `docs/reference/study_overview.md` (section 6), `docs/reference/clean_run_duration.md`,
  `docs/guides/running_and_troubleshooting.md`, `docs/AI_USAGE.md`.
- Verification:
  - The summary-table enrichment matches `compute_alignment_enrichment()` (parquet files) for all
    38/24/24/14 models of the 24 configurations, largest relative difference 1.2·10⁻⁶.
  - The script, run by hand on the frontend with the visualisation environment (outputs in the
    session scratchpad, 13 s), wrote 24 plots and 147 rows; ρ for BLOOMZ, Caption Scene, cosine,
    *k* = 5 checked by hand (0.9); two plots inspected, after which the fixed y-lower limit of 0 was
    dropped because it squeezed every point into a thin band near 1.
  - `snakemake -n` (frontend) schedules 143 jobs: `plot_alignment_enrichment_model_size` 1,
    `plot_concept_alignment_boxplot` 57, `plot_concept_alignment_enrichment_boxplot` 57,
    `plot_spearman_alignment` 27 (renamed outputs) and `all`; nothing upstream.
