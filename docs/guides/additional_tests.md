# Additional tests

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

The additional tests are analyses outside the main pipeline: sensitivity tests whose
results are quoted in the reference pages. They never run with the main workflow: none is included
in `workflow/Snakefile` or in its `rule all`, and a normal run neither builds nor changes them.

Every test follows the same layout:

- **code** in `workflow/additional_tests/<test>/`, with its own `Snakefile` and its scripts in
  `scripts/`;
- **settings** in an overlay `config/<test>.yaml`, added on top of `config/config.yaml` (the image
  overlap has no settings of its own);
- **outputs** only under `results/tests/`, so no main result is touched.

Run each test from the project root, with the base environment active, by passing its Snakefile
with `-s`. The tests read the main pipeline's outputs (brain results, embeddings,
nearest-neighbour files, summary tables), so run the main pipeline first; a test whose inputs are
missing stops. The tests other than the layer-depth test share the numeric environment of the main pipeline
(`workflow/llm_mind_alignment/envs/`), so they build no new environment, and their common
definitions are in `workflow/additional_tests/additional_tests.smk`.

| Test | Snakefile | Method and results |
|---|---|---|
| Layer-depth test | `workflow/additional_tests/layer_depth/Snakefile` | [`model_embeddings.md`](../reference/model_embeddings.md), section 3 |
| Narratives dependency test | `workflow/additional_tests/narratives_dependencies/Snakefile` | [`statistics.md`](../reference/statistics.md), section 8 |
| Duration and length test | `workflow/additional_tests/duration_length_controls/Snakefile` | [`statistics.md`](../reference/statistics.md), section 8 |
| Similarity-type test | `workflow/additional_tests/similarity_type_check/Snakefile` | [`statistics.md`](../reference/statistics.md), section 8 |
| Image overlap test | `workflow/additional_tests/image_overlap/Snakefile` | [`fmri_preprocessing.md`](../reference/fmri_preprocessing.md), "Overlap between the Caption Scene and NSD images" |
| Regional crossover test | `workflow/additional_tests/regional_crossover/Snakefile` | [`regional_crossover.md`](../reference/regional_crossover.md) |

**Running every test.** One after the other, the layer-depth test last because it takes about 5 h 30 min and
needs the GPU (on node5); `|| break` stops at the first test that fails:

```bash
for test in narratives_dependencies duration_length_controls similarity_type_check image_overlap regional_crossover layer_depth; do
    snakemake -s workflow/additional_tests/$test/Snakefile --use-conda --cores 4 --resources gpu=1 || break
done
```

Add `-n` to the `snakemake` line for a dry run. The five tests other than the layer-depth test take about
13 min in all on one core (frontend, 2026-11-26).

**Rerunning.** A test reruns when one of its outputs is missing, one of its inputs is newer (for
example after a rerun of the main pipeline) or one of its settings changes (they are rule
parameters). Snakemake does not see edits to a test's script: after such an edit add
`--forcerun <rule>` (the rule names are given in each section) or delete the test's folder under
`results/tests/`. How Snakemake decides what to rerun
in general is in the [running guide](running_and_troubleshooting.md), section 2.

## 1. Layer-depth test

The test reads the 24 language models of the main analysis (five BLOOMZ, the 16 Gemma models
that are not commented out in `config/config.yaml`, three OpenLLaMA) at a chosen relative depth instead of their last
layer, on Narratives and Nature Stories, and computes the brain-model nearest-neighbour alignment and the
Spearman RSA (whole cortex and language region). Why and how the layer is chosen is in
[`model_embeddings.md`](../reference/model_embeddings.md), section 3.

**Running it.** The test has its own Snakefile, `workflow/additional_tests/layer_depth/Snakefile`, run
from the project root with the base environment active (on node5, or through
`run_snakemake_workflow.sh`, whose last command is this one):

```bash
snakemake -s workflow/additional_tests/layer_depth/Snakefile --cores 4 --resources gpu=1 -n   # dry run
snakemake -s workflow/additional_tests/layer_depth/Snakefile --cores 4 --resources gpu=1
```

**Settings.** `config/layer_depth.yaml` holds the depths (`relative_depths`, now
0.25, 0.5, 0.67 and 0.75), the datasets and the models (`model_subset`); the inner runs add it
on top of `config/config.yaml` without changing it.

**What a depth job does.** The Snakefile has one rule, `run_layer_depth`, with one job per
depth *D* (in percent). Each job reserves 4 cores and the GPU, so the depths run one after the
other, and:

1. links `results/tests/layer_depth_<D>/` to the project's `config/`, `resources/` and
   `workflow/`, and its `results/mind/<dataset>` and `results/language_mind/<dataset>` to the main
   brain results of every dataset of the test, so the brain side is reused, not recomputed or copied
   (`ln -T` stops the job if a real directory is in the way);
2. runs the main workflow in that directory (`snakemake --directory …`) with
   `--config relative_depth=<D/100>` (`relative_depth` is null in `config/config.yaml`),
   `--conda-prefix` set to the project's environments (without it Snakemake would build new ones
   inside the test directory), and `--allowed-rules` listing only the model-side rules:
   `get_embeddings`, `compute_llm_nearest_neighbours`, the alignment, relabelling,
   hypergeometric and empirical p-value and Spearman rules, and the two aggregations. Since the
   brain results and `resources/` are links, a brain, ISC, stimulus or download job would write
   into the main ones; with this list such jobs are never scheduled, the existing brain files
   are plain inputs, and a missing one stops the run.

A full depth is 1540 jobs (24 models, two datasets), all model-side. Without OpenLLaMA (1348
jobs) a depth took 1 h 10 min to 1 h 25 min on node5, and the three OpenLLaMA models add 3–6 min
per depth; the four depths run one after the other, about 5 h 30 min in all.

**Outputs.** Each depth's results go to `results/tests/layer_depth_<D>/results/` with the
main workflow's file names (the depth is only in the directory name); its summary tables are in
`results/tests/layer_depth_<D>/results/tsv_summaries/`. No main result is touched. The last
layer (depth 1) is not run: its embeddings, and every value of its four summary tables, are
identical to the main pipeline's (checked for the 21 BLOOMZ and Gemma models, quantised Gemma
models included), so the final-layer comparison uses the main `results/tsv_summaries/`.
Intermediate depths of the quantised models have run without errors but
have not been checked further.

**Rerunning.** A depth job runs only when one of its four summary tables is missing. After a
code or settings change, add `--forcerun run_layer_depth`: every depth job then starts its
inner run, which recomputes only what Snakemake sees as outdated ([running guide](running_and_troubleshooting.md), section 2). Edits to a script
that Snakemake does not see, such as `get_embeddings.py`, are not picked up that way: first delete
the outputs of the first affected rule in each depth directory, for example
`results/tests/layer_depth_*/results/language_models/*/embeddings/*.parquet` after a change
to `get_embeddings.py`, which recomputes every embedding and everything downstream. Copy
`results/tests/layer_depth_<D>/results/tsv_summaries/` elsewhere first to keep the previous
numbers.

**Adding models without recomputing the others.** The embeddings of the 21 BLOOMZ and Gemma models
were computed before the `get_embeddings` rule received its depth flag as a parameter, so their
Snakemake records differ from the current rule: a `--forcerun run_layer_depth` recomputes
every embedding of every depth (about 5 h 30 min), although the vectors would not change. To
compute only missing outputs and the summary tables, run each depth's inner workflow directly,
with `--rerun-triggers mtime input` (this is how OpenLLaMA was added):

```bash
for D in 25 50 67 75; do
    snakemake results/tsv_summaries/all_model_brain_alignment_scores.tsv \
        results/tsv_summaries/all_model_brain_alignment_scores_language.tsv \
        results/tsv_summaries/all_spearman_alignment_scores.tsv \
        results/tsv_summaries/all_spearman_alignment_scores_language.tsv \
        --directory results/tests/layer_depth_$D \
        --configfile "$PWD/config/layer_depth.yaml" \
        --config relative_depth=$(python3 -c "print(f'{$D/100:g}')") \
        --use-conda --conda-prefix "$PWD/.snakemake/conda" \
        --cores 4 --resources gpu=1 \
        --rerun-triggers mtime input \
        --allowed-rules get_embeddings compute_llm_nearest_neighbours compute_llm_mind_alignment_score relabel_llm_similarity_and_compute_relabelled_llm_alignment_score compute_empirical_p_value compute_hypergeometric_p_value aggregate_all_p_value_outputs compute_spearman_alignment_with_empirical_p_value aggregate_all_spearman_alignment_scores \
        || break
done
```

## 2. Narratives dependency test

Tests whether the whole-cortex Spearman RSA of the language models on Narratives survives the
dependencies between the 18 units (shared story, speaker or source). Method and results:
[`statistics.md`](../reference/statistics.md), section 8, "Dependencies between the Narratives
units".

**Running it.**

```bash
snakemake -s workflow/additional_tests/narratives_dependencies/Snakefile --use-conda --cores 1
```

**Settings.** `config/narratives_dependencies.yaml` lists the four blocks of related units
(`unit_blocks`) and the five unrelated units (`unrelated_units`); together they must name every
unit once. The relabellings and the seed are the main config's `number_of_relabellings` and
`random_seed`, so the tests reuse the pipeline's permutation stream.

**What it does.** One rule, `narratives_dependencies`. It rebuilds the brain and model similarity
matrices as the Spearman RSA rule does (capped model embeddings) and first checks every full RSA
coefficient against `results/tsv_summaries/all_spearman_alignment_scores.tsv`, stopping if one
differs by more than 10⁻⁵. Then it computes the restricted permutations (240 per pairing of the two
2-unit blocks), the leave-out RSA (without each unit, each block and both 2-unit blocks; one unit
per block; without the pairs inside a block) and the mean similarity rank of each unit. Runs in
about 8 min.

**Outputs**, in `results/tests/narratives_dependencies/`:

- `restricted_permutations.tsv`: one row per pairing, similarity type and model: the coefficient,
  the published and restricted p-values, the restricted q-value, the null means and the counts at
  least as large among the unswapped and swapped permutations;
- `leave_out.tsv`: one row per check and similarity type: units, pairs, median, minimum and maximum
  coefficient over the models, tests and tests with q < 0.05 (no test for the check without the
  pairs inside a block);
- `unit_distinctness.tsv`: one row per unit: the mean rank of its similarities to the other units,
  in the brain and in the median model ranks, per similarity type.

**Rerunning.** `--forcerun narratives_dependencies`.

## 3. Duration and length test

Tests whether story duration or length explains the whole-cortex Spearman RSA of the language models
on Narratives and Nature Stories. Method and results: [`statistics.md`](../reference/statistics.md),
section 8, "Duration and length".

**Running it.**

```bash
snakemake -s workflow/additional_tests/duration_length_controls/Snakefile --use-conda --cores 1
```

**Settings.** `config/duration_length_controls.yaml` lists the datasets with the repetition time
of their scans (`repetition_times`: Narratives 1.5 s, Nature Stories 2.0 s), which turns a scan
length in volumes into minutes. Relabellings and seed come from the main config.

**What it does.** One rule, `duration_length_controls`. For each dataset it reads each story's
shortest scan from the parcel time series listed in `results/mind/<dataset>/manifests/isc_manifest.tsv`,
checks every published RSA coefficient as the dependency test does, and computes the partial RSA
controlling for duration and for each model's token count, the association of duration with the
brain and model geometries, and the association of mean ISC with duration, tokens and (Narratives)
the number of subjects. Runs in about 2 min.

**Outputs**, in `results/tests/duration_length_controls/`:

- `stimuli.tsv`: one row per story: scan length in volumes and minutes, subjects, mean ISC, mean
  token count over the models;
- `models.tsv`: one row per dataset, similarity type and model: published, duration-model, and
  partial (duration, tokens) coefficients with p- and q-values (BH across the models of a dataset
  and similarity type);
- `brain_duration.tsv`: the association of duration with the brain geometry, per dataset and
  similarity type;
- `mean_isc_associations.tsv`: the two-sided permutation tests of mean ISC against each property.

**Rerunning.** `--forcerun duration_length_controls`.

## 4. Similarity-type test

Tests why local alignment on Narratives (*k* = 5) is significant for almost every language model
under Spearman similarity but for few under cosine or Pearson. Method and results:
[`statistics.md`](../reference/statistics.md), section 8, "Why the similarity types differ on
Narratives".

**Running it.**

```bash
snakemake -s workflow/additional_tests/similarity_type_check/Snakefile --use-conda --cores 1
```

**Settings.** `config/similarity_type_check.yaml`: the number of subsampling draws
(`subsample_draws`, 20), the number of highest-ISC parcels left out (`top_parcels`, 17) and the
offset of the log transform (`log_offset`, 0.05). The subsample size is not a setting: it is the
smallest story's number of subjects (14). *k* is the Narratives `number_of_neighbours` of the main
config.

**What it does.** One rule, `similarity_type_check`. It recomputes the brain neighbours and the
model-level alignment of every language model under four conditions (published ISC, every story
subsampled to the same number of subjects, without the highest-ISC parcels, log ISC) and tests them
with the pipeline's relabelling null. Two checks stop it if they fail: the published condition must
reproduce the pipeline's alignment and p-values
(`results/tsv_summaries/all_model_brain_alignment_scores.tsv`), and the ISC recomputed from the
parcel time series must match the published ISC. Runs in about 1 min 30 s.

**Outputs**, in `results/tests/similarity_type_check/`:

- `summary.tsv`: one row per condition and similarity type: the median observed alignment and the
  number of models with p < 0.05 and q < 0.05 (median, minimum and maximum over the draws);
- `isc_properties.tsv`: the median skewness of the ISC vectors before and after the log transform,
  the variance share of the highest-ISC parcels and their label IDs (1-based Schaefer IDs), the
  number of ISC values at most 0 and the smallest value, and the subsample size.

**Rerunning.** `--forcerun similarity_type_check`.

## 5. Image overlap test

Counts the COCO images shared by the retained NSD and Caption Scene stimuli. Results:
[`fmri_preprocessing.md`](../reference/fmri_preprocessing.md), "Overlap between the Caption Scene
and NSD images".

**Running it.**

```bash
snakemake -s workflow/additional_tests/image_overlap/Snakefile --use-conda --cores 1
```

**Settings.** None of its own: it reads `nsddata/experiments/nsd/nsd_stim_info_merged.csv` under
the NSD `dataset_dir` and `Stimulus_index.tsv` next to the Caption Scene image folder, both from
the main config.

**What it does.** One rule, `image_overlap`, which matches the retained images of each dataset (the
concepts of `results/mind/{nsd_data,caption_scene}/isc_dataframe.parquet`) by COCO image ID, and
also compares the full stimulus sets. Runs in a few seconds.

**Outputs.** `results/tests/image_overlap/image_overlap.tsv`: one row per count (retained images,
images retained in both datasets and their COCO IDs, full-set overlaps).

**Rerunning.** `--forcerun image_overlap`.

## 6. Regional crossover test

A collaborator's analysis, reproduced as closely as possible: on Caption Scene, vision and language
models in the visual and language regions; on Narratives, the language models in the language
region and the whole cortex. Method and results:
[`regional_crossover.md`](../reference/regional_crossover.md).

**Running it.**

```bash
snakemake -s workflow/additional_tests/regional_crossover/Snakefile --use-conda --cores 1
```

**Settings.** `config/regional_crossover.yaml`: the similarity type (`similarity_type`, Spearman
only) and, per dataset, the bootstrap iterations and seed (`bootstrap`: Caption Scene 2000 and
20261109, Narratives 1000 and 42), all the collaborator's values. The neighbour files are read as
stored, so only at the largest configured *k*.

**What it does.** Two rules, one per original script: `regional_crossover_caption_scene` and
`regional_crossover_narratives` (target rule `all_regional_crossover`). They follow the scripts
step by step, including their random streams, so they reproduce their numbers exactly. Runs in
about 1 min.

**Outputs**, in `results/tests/regional_crossover/`:

- `regional_crossover_caption_scene.tsv`: the cells A–D and the contrasts A − C and
  (A + D) − (B + C) with their 95% bootstrap intervals;
- `regional_crossover_caption_scene_families.tsv`: median, minimum, maximum and number of models
  of each family in cells A and C;
- `regional_crossover_narratives.tsv`: the language region, the whole cortex and their difference
  with its 95% bootstrap interval.

**Rerunning.** `--forcerun regional_crossover_caption_scene regional_crossover_narratives`.

## Changes

### 2026-11-25 17:30 — guide created

Created to hold, for every test outside the main pipeline, how to run it, its settings, what it
does, its outputs and how to rerun it. The layer-depth pilot section moved here from the running
guide, with the pilot's Snakefile now at `workflow/additional_tests/layer_depth_pilot/`; its
content is otherwise unchanged.

### 2026-11-26 12:00 — five tests added

Added the Narratives dependency checks, the duration and length controls, the similarity-type
check, the image overlap and the regional crossover, which used to be one-off scripts outside the
repository, with one section each; the introduction gains the table of every test, the command
that runs them all and how they are rerun.

### 2026-11-26 16:40 — pilot runs four depths

Section 1: the pilot no longer runs the last layer (depth 1), whose results were identical to the
main ones for its 21 models; the depths, the run time (about 5 h instead of 6 h 30 min) and the
final-layer comparison, now taken from the main results, are updated, as is the run time quoted
in the introduction.

### 2026-11-27 11:45 — OpenLLaMA in the pilot

Section 1: the pilot covers the three OpenLLaMA models too (24 models, 1540 jobs per depth, about
5 h 30 min in all). A new paragraph explains why a forced rerun recomputes every embedding and how
to add models with `--rerun-triggers mtime input` instead, as was done for OpenLLaMA.

### 2026-11-27 13:40 — every additional test called a test

The layer-depth pilot is now called the layer-depth test, and the other tests are named the same way: Narratives dependency test, duration and length test, similarity-type test, image overlap test and regional crossover test (table, section headings and introduction). File, rule and directory names are unchanged (`layer_depth_pilot`, `narratives_dependencies`, …).

### 2026-11-27 15:25 — layer-depth file and directory names without "pilot"

The test's Snakefile is now `workflow/additional_tests/layer_depth/Snakefile`, its settings
`config/layer_depth.yaml`, its rule `run_layer_depth` and its outputs
`results/tests/layer_depth_<D>/`; every path, command and rule name above follows.
