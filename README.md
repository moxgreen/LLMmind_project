# LLMmind

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](docs/AI_USAGE.md).*

A Snakemake pipeline that measures how well the internal representations of
pretrained language and vision models align with human brain activity, using
nearest-neighbour structure in representational space as the basis for
comparison. (Directory and rule names say `llm` for any model, language or
vision.)

For each (dataset, model, similarity metric, neighbourhood size) combination,
the pipeline:

1. Extracts per-stimulus brain representations from fMRI data: for each
   stimulus, the inter-subject correlation (ISC) of 200 brain parcels.
2. Extracts model embeddings for the same stimuli from a set of pretrained
   language and vision models.
3. Computes nearest-neighbour graphs in both spaces (brain and model) under a
   chosen similarity metric (cosine, Pearson or Spearman).
4. Scores brain-model alignment as the overlap between the two
   nearest-neighbour graphs, with empirical (permutation-based) and
   hypergeometric significance testing.
5. Also computes model-model alignment (how similar two models'
   representational geometries are) and Spearman rank-correlation alignment as
   a complementary metric.
6. Produces summary tables and plots (heatmaps, line plots, boxplots) across
   models, datasets and similarity metrics.

## Documentation

- [`docs/guides/running_and_troubleshooting.md`](docs/guides/running_and_troubleshooting.md)
  — how to run parts of the pipeline, when Snakemake reruns a job, the
  settings that change many results, the software environments, model
  limitations and what to do when a run fails
- [`docs/guides/additional_tests.md`](docs/guides/additional_tests.md)
  — how to run each test outside the main pipeline (the layer-depth test, the
  robustness tests, the image overlap test, the regional crossover test): settings,
  outputs and reruns
- [`docs/reference/study_overview.md`](docs/reference/study_overview.md)
  — start here to write the article: study design, datasets, models, parameters,
  which page covers each part of the article, which numbers the workflow
  reproduces, limitations and references. The `docs/reference/` pages are the
  main source for the article
- [`docs/reference/fmri_preprocessing.md`](docs/reference/fmri_preprocessing.md)
  — what each dataset's authors did to the BOLD data before this workflow, and
  what the workflow itself does, up to the ISC (a source for the methods
  section)
- [`docs/reference/nature_stories_stimuli.md`](docs/reference/nature_stories_stimuli.md)
  — where the Nature Stories transcripts come from (a separate release from
  the fMRI data) and the check that both describe the same stimuli
- [`docs/reference/model_embeddings.md`](docs/reference/model_embeddings.md)
  — how each model turns a stimulus into one vector: chunking, pooling
  (including the BOS token) and the CLS token of vision models (a source for
  the methods section)
- [`docs/reference/brain_regions.md`](docs/reference/brain_regions.md)
  — the language and visual brain regions: which parcels, how their ISC is
  taken from the whole-cortex ISC, and where their results go
- [`docs/reference/statistics.md`](docs/reference/statistics.md)
  — alignment scores, the relabelling and Spearman nulls, the empirical and
  hypergeometric tests, enrichment, the Benjamini-Hochberg families, and what
  every figure shows and how it is laid out (a source for the methods section)
- [`docs/reference/regional_crossover.md`](docs/reference/regional_crossover.md)
  — the regional crossover test, a collaborator's analysis: every model class in
  every brain region on Caption Scene, and language region vs whole cortex on
  Narratives, with its limits
- [`docs/reference/clean_run_duration.md`](docs/reference/clean_run_duration.md)
  — how long a clean run takes on node5 (about 33 h), rule by rule
- [`docs/changelog/developers/`](docs/changelog/developers/) and
  [`docs/changelog/users/`](docs/changelog/users/) — one file per day with
  changes, technical and plain-language. Each file name lists the kinds of
  change made that day (`new_feature`, `bugfix`, `optimisation`, `refactor`,
  `removal`, `documentation`)
- [`docs/AI_USAGE.md`](docs/AI_USAGE.md) — how AI coding assistants were used
  in this project, and the date and model of the latest AI edit of every file

## Repository layout

```
config/                     Snakemake configuration (config.yaml; one overlay per additional test, such as layer_depth.yaml)
workflow/
  Snakefile                 Top-level Snakefile: wires up all modules and the `all` rule
  libraries/                Shared Python helper modules (similarity, alignment,
                             nearest-neighbours, statistics, plotting utilities)
  dataset_processing/       Per-dataset rules: turn raw fMRI + stimuli into
                             brain representations (one subdirectory per dataset)
    caption_scene_dataset/
    narratives_dataset/
    nature_stories_dataset/
    nsd_data_dataset/
  isc_nearest_neighbours/   Nearest-neighbour graphs over brain (ISC) representations
  llm_nearest_neighbours/   Model download + embedding extraction + nearest-neighbour graphs
  llm_mind_alignment/       Brain-model alignment scoring and significance testing
  llm_llm_alignment/        Model-model alignment scoring
  spearman_alignment/       Spearman rank-correlation alignment (model- and concept-level)
  visualisation/            Plotting rules (heatmaps, line plots, boxplots)
  additional_tests/         Tests outside the main pipeline, one folder and
                             Snakefile per test: layer_depth/,
                             narratives_dependencies/,
                             duration_length_controls/,
                             similarity_type_check/, image_overlap/,
                             regional_crossover/; additional_tests.smk holds
                             their shared definitions
  envs/                     Base environment for running Snakemake itself
                             (LLMmind_project_environment.yaml spec + the
                             materialized LLMmind_project/ conda prefix,
                             which is not tracked in git)
resources/                  Inputs — not tracked in git
  atlases/                  Downloaded brain parcellation atlases and MNI template
  datasets/                 Raw dataset inputs (fMRI + stimuli)
  models/                   Downloaded pretrained model weights
results/                    Pipeline outputs — not tracked in git
docs/
  guides/                   How to run the pipeline and fix failed runs
  reference/                Methods: fMRI processing, embeddings, statistics; run duration
  changelog/                Developer- and user-facing changelogs, one file per day
  AI_USAGE.md               AI assistance policy and per-file AI edit list
```

## Modules

The pipeline is split into Snakemake modules under `workflow/`, each included
from the top-level `Snakefile` and each corresponding to one step above.

### `dataset_processing/<dataset>/`

One subdirectory per dataset. Each builds manifests that match scan files to
stimuli and exclude unusable subjects, runs and stimuli; extracts the mean
signal of each Schaefer parcel; and computes the leave-one-subject-out ISC per
stimulus and parcel. It also prepares the matching stimuli (transcripts for
the language datasets, images for the vision datasets) for the embedding step.
The details, dataset by dataset, are in
[`fmri_preprocessing.md`](docs/reference/fmri_preprocessing.md).

Dropped stimuli are listed in the dataset's `excluded_stimuli` file, which
both the brain and the model side skip (see
[`model_embeddings.md`](docs/reference/model_embeddings.md)).

### `isc_nearest_neighbours/`

Takes the per-dataset ISC vectors, computes stimulus-stimulus similarity and
builds the brain-side nearest-neighbour graphs, for the whole cortex and for
the region of each stimulus type, whose ISC it takes from the whole-cortex one
(see [`brain_regions.md`](docs/reference/brain_regions.md)).

### `llm_nearest_neighbours/`

Downloads each configured model (`download_pretrained_llm`), extracts its
embeddings for the same stimuli (`get_embeddings`, see
[`model_embeddings.md`](docs/reference/model_embeddings.md)), computes
embedding-embedding similarity and builds the model-side nearest-neighbour
graphs.

### `llm_mind_alignment/`

Scores brain-model alignment as the overlap between the brain and model
nearest-neighbour graphs, with empirical (permutation-based) and
hypergeometric significance testing.

### `llm_llm_alignment/`

Scores model-model alignment with the same tests, reusing the
`llm_mind_alignment/` p-value scripts. Pairs are formed between
*(model, stimulus type)* entries, so on a dataset with both text and image
stimuli a language model is also compared with a vision model.

### `spearman_alignment/`

A complementary alignment metric: the Spearman rank correlation between the
brain's and the model's similarity structures, at model and concept level,
with empirical significance testing.

### `visualisation/`

Produces the plots listed under [Outputs](#outputs).

### `libraries/`

Shared Python helper modules used across all of the above.

## Datasets

Four naturalistic fMRI datasets, each configured under its own key in
`config/config.yaml`:

- `caption_scene` — image/caption viewing task (language + vision stimuli)
- `narratives` — spoken story listening (language stimuli)
- `nature_stories` — spoken story listening (language stimuli)
- `nsd_data` — Natural Scenes Dataset (vision stimuli)

Each entry defines the stimuli directories (by modality), subject count,
exclusion lists, acquisition parameters (TR, event duration, etc.) and the
neighbourhood sizes (`number_of_neighbours`) to evaluate. Which stimuli are
kept is described in
[`fmri_preprocessing.md`](docs/reference/fmri_preprocessing.md).

## Input data

None of the raw fMRI/stimuli datasets are tracked in git — they must be
present under `resources/datasets/` before the first run. `resources/models/`
(pretrained model weights) and `resources/atlases/` (brain atlases and the MNI
template, see [`fmri_preprocessing.md`](docs/reference/fmri_preprocessing.md))
do **not** need to be supplied manually: they are downloaded automatically
the first time they're needed (internet access is required on first run).
`results/` is fully generated by the pipeline and can be empty/absent.

The four datasets come from these public releases:

- **Caption Scene**: "CSD: Caption Scene Dataset", ScienceDB, DOI
  `10.57760/sciencedb.27580` (Li et al., *Sci. Data*, 2026,
  doi:10.1038/s41597-026-07248-6). The release has one folder per version;
  the files below are from version `V1`.
- **Narratives**: OpenNeuro `ds002345` (DOI
  `10.18112/openneuro.ds002345.v1.1.4`; Nastase et al., *Sci. Data* 8, 250,
  2021), downloaded with DataLad from
  `https://datasets.datalad.org/labs/hasson/narratives`, the authors' DataLad
  copy, which includes the `derivatives/afni-smooth/` files and
  `code/scan_exclude.json`.
- **Nature Stories**: "Nature story listening 3T fMRI data", G-Node GIN, DOI
  `10.12751/g-node.t4wew2` (archive `10.12751_g-node.t4wew2.zip`). The
  TextGrids come from OpenNeuro `ds003020` (see
  [`nature_stories_stimuli.md`](docs/reference/nature_stories_stimuli.md)).
- **NSD**: Natural Scenes Dataset (Allen et al., *Nat. Neurosci.* 25, 116–126,
  2022), public AWS S3 bucket `s3://natural-scenes-dataset` (region
  `us-east-2`, no AWS account needed). Its terms of use require filling in the
  NSD Data Access Agreement at <https://naturalscenesdataset.org/>.

They need the following raw files, at these exact paths relative to
`resources/datasets/`:

**Caption Scene dataset** (`caption_scene_dataset/`)

- Preprocessed BOLD:
  `V1/derivatives/pp_data/sub-*/func/sub-*_ses-*_task-CSD_run-*.nii.gz`
- Run/event tables:
  `V1/stimuli/CSD/sub-{subject}/subject{subject}_run{run}.txt`
- Stimulus images:
  `V1/stimuli/COCO_CN/All_images_480/`
- Caption table:
  `V1/stimuli/COCO_CN/Translated_Image_Caption_pairs.tsv`
- T1w scans, used to register each subject to MNI:
  `V1/sub-{subject}/anat/sub-{subject}_ses-01_run-001_T1w.nii.gz`

**Narratives dataset** (`narratives_dataset/`)

- Preprocessed BOLD:
  `derivatives/afni-smooth/sub-{subject}/func/sub-{subject}_task-{task}{run_tag}_space-MNI152NLin2009cAsym_res-native_desc-clean_bold.nii.gz`
- Original transcripts:
  `stimuli/transcripts/*_transcript.txt`
- Scan exclusion metadata:
  `scan_exclude.json`

**Nature Stories dataset** (`nature_stories_dataset/`)

- Subject BOLD responses:
  `responses/S01_BOLD.hdf` … `responses/S11_BOLD.hdf`
- Subject mapper files:
  `mappers/S01_mappers.hdf` … `mappers/S11_mappers.hdf`
- Run/story onset metadata:
  `responses/new_run_onsets.json`
- Source TextGrid stimulus files:
  `stimuli/textgrids/<story>.TextGrid`, from OpenNeuro `ds003020`, not from
  the fMRI archive (see
  [`nature_stories_stimuli.md`](docs/reference/nature_stories_stimuli.md))

**NSD dataset** (`nsd_data_dataset/`)

- Functional design files, subjects `subj01`–`subj08`:
  `nsddata_timeseries/ppdata/subjXX/func1pt8mm/design/design_session*_run*.tsv`
- Matching BOLD timeseries:
  `nsddata_timeseries/ppdata/subjXX/func1pt8mm/timeseries/timeseries_session*_run*.nii.gz`
- Stimulus images:
  `nsddata_stimuli/stimuli/nsd/nsd_stimuli.hdf5`
- Functional-to-MNI mapping data, used internally (via the `nsdcode`
  package) to register each subject's BOLD data into MNI space:
  `nsddata/ppdata/subjXX/transforms/`

Everything else under a dataset directory (e.g. `.stimuli_ready`,
`excluded_stimuli.txt`, renamed/derived transcripts) is generated by the
pipeline itself and must **not** be supplied manually. In particular,
`excluded_stimuli.txt` is rewritten from the stimulus-inclusion rules
(see [`dataset_processing/<dataset>/`](#dataset_processingdataset)); do
not edit it by hand to exclude stimuli.

### Organising the input data on disk

`resources/datasets/` is expected to contain one directory per dataset,
named exactly as above:

```
resources/datasets/
├── caption_scene_dataset/
├── narratives_dataset/
├── nature_stories_dataset/
└── nsd_data_dataset/
```

The raw data were downloaded with an auxiliary Snakemake workflow that is
not part of this repository. Its download rules are left out of this
pipeline on purpose: the datasets are very large, and a run should not fill a
disk by mistake. To reproduce the analysis, download the files listed above
from the public releases of the four datasets and place them in these
directories, at the paths given above. A dataset directory may also be a
symbolic link to wherever the data are stored.

### Input files that are not plain downloads

The download workflow obtains three of the files listed above from the
public releases with an extra step, which must be repeated by hand when the
data are downloaded some other way:

- **`caption_scene_dataset/V1/stimuli/CSD/`**: extracted from the archive
  `V1/stimuli/CSD.rar` of the Caption Scene release, inside `V1/stimuli/`
  (for example `unrar x CSD.rar`).
- **`narratives_dataset/scan_exclude.json`**: a copy of
  `code/scan_exclude.json` from the Narratives DataLad dataset, where it is
  tracked in git and needs no `datalad get`.
- **`nature_stories_dataset/responses/new_run_onsets.json`**: a corrected
  copy of `responses/run_onsets.json` from the Nature Stories archive. The
  dataset README states that each story in `zRresp` was z-scored on its own
  before concatenation, but with the original boundaries 7 of the 10 training
  stories are not z-scored. The workflow searches, around each original
  boundary, for the one that leaves every story segment z-scored. This shifts
  five boundaries by 1–2 TRs (the total, 3737 TRs, is unchanged):

  | Story | Original onset, length | Corrected onset, length |
  |---|---|---|
  | alternateithicatom | 0, 345 | 0, 343 |
  | avatar | 345, 366 | 343, 367 |
  | howtodraw | 711, 353 | 710, 354 |
  | naked | 2252, 421 | 2252, 422 |
  | odetostepfather | 2673, 406 | 2674, 404 |
  | souls | 3079, 355 | 3078, 355 |
  | undertheinfluence | 3434, 303 | 3433, 304 |

  With these boundaries every story segment of `zRresp` has, voxel by voxel,
  mean 0 and standard deviation 1 to machine precision (about 1e-14) in all
  11 subjects, and moving any boundary by one TR breaks this, so the
  corrected values can be re-derived from the public `*_BOLD.hdf` files.

One file is not in any public release:
`caption_scene_dataset/V1/stimuli/COCO_CN/Translated_Image_Caption_pairs.tsv`,
the English translation of the captions (the release has the Chinese captions
only, in `Image_caption_pairs.tsv`). It was obtained from the dataset
authors.

## Models

Models are declared under `models:` in `config/config.yaml`, each with a
Hugging Face identifier, modality (`language` or `vision`), optional
quantization method and parameter count. Currently configured: the BLOOMZ,
OpenLLaMA and Gemma (Gemma, Gemma 2, Gemma 3, Gemma 3n, Gemma 4) language
model families; the CLIP, DINOv2 and ImageNet-21K ViT vision model families
(full list in [`study_overview.md`](docs/reference/study_overview.md), section 3).
Models are downloaded on demand by the `llm_nearest_neighbours` module.

A model runs on the stimulus type of a dataset that matches its modality:
`language` models on text, `vision` models on images. Every output file names
a model together with its stimulus type, as `<model>-<stimuli_type>` (for
example `clip_b-vision`). To add a model, add its block to the config and
rerun; multimodal and mixture-of-experts models are not supported (see the
[guide](docs/guides/running_and_troubleshooting.md#5-model-limitations)).

## Setup

The project uses a base environment for running Snakemake itself at
`workflow/envs/LLMmind_project`, specified by
`workflow/envs/LLMmind_project_environment.yaml` (Python and `snakemake`).

```bash
# create the base environment from its spec (first time only)
conda env create -f workflow/envs/LLMmind_project_environment.yaml -p workflow/envs/LLMmind_project

# activate it (see .envrc for the expected path)
conda activate workflow/envs/LLMmind_project
```

If you use [direnv](https://direnv.net/), `.envrc` activates this environment
automatically when you `cd` into the project. Every rule that runs a script declares its own
pinned `conda:` environment (`workflow/*/envs/*.yaml`), which Snakemake
creates automatically with `--use-conda`; the few small rules that run no
script (lists, manifests, flag files, one download and one copy) run in the
base environment (see the
[guide](docs/guides/running_and_troubleshooting.md#4-software-environments)).

## Running the pipeline

From the project root, with the base environment active:

```bash
# dry run to see what would be executed
snakemake --use-conda --cores <N> -n

# run everything
snakemake --use-conda --cores <N>
```

The additional tests are outside the main pipeline and have their own
Snakefiles in `workflow/additional_tests/`. To run them all, one after the
other (the layer-depth test last: about 5 h 30 min on the GPU):

```bash
for test in narratives_dependencies duration_length_controls similarity_type_check image_overlap regional_crossover layer_depth; do
    snakemake -s workflow/additional_tests/$test/Snakefile --use-conda --cores 4 --resources gpu=1 || break
done
```

How to run each one, its settings and its outputs are in the
[additional-tests guide](docs/guides/additional_tests.md).

All pipeline behaviour (datasets, models, similarity metrics, neighbourhood
sizes, number of permutations) is set in `config/config.yaml`; no code changes
are needed to add a model or adjust a dataset. Partial runs, rerun behaviour,
the settings that rebuild many results, the configuration checks and the
fixes for common failures are in
[`running_and_troubleshooting.md`](docs/guides/running_and_troubleshooting.md).

## Outputs

Key outputs land under `results/`. Per-configuration files carry the
similarity metric (`cosine`, `pearson` or `spearman`) in their name; the
combined summary tables have a `similarity_type` column instead.

- `results/alignment_scores/` — per-(dataset, model, similarity, k) alignment
  scores with per-concept empirical and hypergeometric p-values, brain-model
  and model-model, and the relabelled scores in
  `relabelled_common_neighbours/` (see
  [`statistics.md`](docs/reference/statistics.md)).
- `results/spearman_alignment_scores/` — per-(dataset, model, similarity)
  Spearman alignment with its empirical p-value, one `_model_level` and one
  `_concept_level` TSV per configuration.
- `results/tsv_summaries/all_model_brain_alignment_scores.tsv`,
  `results/tsv_summaries/all_model_model_alignment_scores.tsv`,
  `results/tsv_summaries/all_spearman_alignment_scores.tsv` — combined summary tables
  across all configurations, in long format, with the model-level test
  `model_level_empirical_p_value`. Their columns and which p-values are tests
  are described in [`statistics.md`](docs/reference/statistics.md).
- `results/tsv_summaries/model_size_within_family_spearman.tsv` — Spearman's ρ
  of the enrichment against parameter count within each model family, per
  dataset, similarity type and *k* (section 8 of
  [`statistics.md`](docs/reference/statistics.md)).
- `results/pictures/` — every plot and heatmap, one subfolder per plot type:
  `alignment_heatmaps/`, `alignment_p_value_heatmaps/`,
  `alignment_lineplots/`, `concept_alignment_boxplots/`,
  `alignment_enrichment_lineplots/`,
  `concept_alignment_enrichment_boxplots/`,
  `spearman_alignment_lineplots/`, `concept_spearman_alignment_boxplots/`,
  `similarity_comparison_lineplots/`, `model_size_lineplots/`.
  What each figure shows and the conventions shared by all plots (model
  order, colours, asterisks, null intervals, axes) are in section 7 of
  [`statistics.md`](docs/reference/statistics.md).
- Region results: every brain-model output above (alignment scores, Spearman
  scores, the brain-model and Spearman summary tables, the plots except the
  heatmaps) also exists for the language and the visual region, with
  `_language` or `_vision` appended to the directory, table or plot-folder name
  (for example `results/alignment_scores_language/`,
  `results/tsv_summaries/all_model_brain_alignment_scores_vision.tsv`,
  `results/pictures/alignment_lineplots_language/`); the region ISC is in
  `results/language_mind/` and `results/vision_mind/` (see
  [`brain_regions.md`](docs/reference/brain_regions.md)).
- `results/mind/nature_stories/qc/textgrid_check.tsv` and
  `textgrid_check_unexplained_words.tsv` — the check that the Nature Stories
  transcripts match the word and phoneme timing of the fMRI release, built only
  by `snakemake --use-conda --cores 1 all_nature_stories_dataset` (see section 4
  of [`nature_stories_stimuli.md`](docs/reference/nature_stories_stimuli.md)).
- `results/tests/<test>/` — the tables of the additional tests, written only
  when a test is run (see the
  [additional-tests guide](docs/guides/additional_tests.md)).
