# 2026-11-26 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Five one-off analyses turned into additional tests under `workflow/additional_tests/`; documentation updated with their numbers (new feature, documentation)

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
