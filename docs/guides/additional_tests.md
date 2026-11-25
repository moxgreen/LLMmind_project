# Additional tests

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

The additional tests are analyses outside the main pipeline: sensitivity checks and controls whose
results are quoted in the reference pages. They never run with the main workflow: none is included
in `workflow/Snakefile` or in its `rule all`, and a normal run neither builds nor changes them.

Every test follows the same layout:

- **code** in `workflow/additional_tests/<test>/`, with its own `Snakefile`;
- **settings** in an overlay `config/<test>.yaml`;
- **outputs** only under `results/tests/`, so no main result is touched.

Run each test from the project root, with the base environment active, by passing its Snakefile
with `-s`. The tests read the main pipeline's outputs (brain results, nearest-neighbour files,
summary tables), so run the main pipeline first; a test whose inputs are missing stops. How
Snakemake decides what to rerun is in the [running guide](running_and_troubleshooting.md),
section 2.

| Test | Snakefile | Method and results |
|---|---|---|
| Layer-depth pilot | `workflow/additional_tests/layer_depth_pilot/Snakefile` | [`model_embeddings.md`](../reference/model_embeddings.md), section 3 |

## 1. Layer-depth pilot

The pilot reads the five BLOOMZ models and the 16 Gemma models (every Gemma entry of
`config/config.yaml` that is not commented out) at a chosen relative depth instead of their last
layer, on Narratives and Nature Stories, and computes the brain-model nearest-neighbour alignment and the
Spearman RSA (whole cortex and language region). Why and how the layer is chosen is in
[`model_embeddings.md`](../reference/model_embeddings.md), section 3.

**Running it.** The pilot has its own Snakefile, `workflow/additional_tests/layer_depth_pilot/Snakefile`, run
from the project root with the base environment active (on node5, or through
`run_snakemake_workflow.sh`, whose last command is this one):

```bash
snakemake -s workflow/additional_tests/layer_depth_pilot/Snakefile --cores 4 --resources gpu=1 -n   # dry run
snakemake -s workflow/additional_tests/layer_depth_pilot/Snakefile --cores 4 --resources gpu=1
```

**Settings.** `config/layer_depth_pilot.yaml` holds the depths (`relative_depths`, now
0.25, 0.5, 0.67, 0.75 and 1), the datasets and the models (`model_subset`); the inner runs add it
on top of `config/config.yaml` without changing it.

**What a depth job does.** The Snakefile has one rule, `run_layer_depth_pilot`, with one job per
depth *D* (in percent). Each job reserves 4 cores and the GPU, so the depths run one after the
other, and:

1. links `results/tests/layer_depth_pilot_<D>/` to the project's `config/`, `resources/` and
   `workflow/`, and its `results/mind/<dataset>` and `results/language_mind/<dataset>` to the main
   brain results of every pilot dataset, so the brain side is reused, not recomputed or copied
   (`ln -T` stops the job if a real directory is in the way);
2. runs the main workflow in that directory (`snakemake --directory …`) with
   `--config relative_depth=<D/100>` (`relative_depth` is null in `config/config.yaml`),
   `--conda-prefix` set to the project's environments (without it Snakemake would build new ones
   inside the pilot directory), and `--allowed-rules` listing only the model-side rules:
   `get_embeddings`, `compute_llm_nearest_neighbours`, the alignment, relabelling,
   hypergeometric and empirical p-value and Spearman rules, and the two aggregations. Since the
   brain results and `resources/` are links, a brain, ISC, stimulus or download job would write
   into the main ones; with this list such jobs are never scheduled, the existing brain files
   are plain inputs, and a missing one stops the run.

A full depth is 1348 jobs (21 models, two datasets), all model-side, and takes about
1 h 10 min to 1 h 25 min on node5; the five depths run one after the other, about 6 h 30 min in all.

**Outputs.** Each depth's results go to `results/tests/layer_depth_pilot_<D>/results/` with the
main workflow's file names (the depth is only in the directory name); its summary tables are in
`results/tests/layer_depth_pilot_<D>/results/tsv_summaries/`. No main result is touched. The 100%
run reads the same vectors as the main pipeline and serves as the final-layer comparison
computed with the same code: its embeddings are identical to the main pipeline's for all 21
models, quantised Gemma models included, so its summary tables differ from the main ones only by
the cap of model values. Intermediate depths of the quantised models have run without errors but
have not been checked further.

**Rerunning.** A depth job runs only when one of its four summary tables is missing. After a
code or settings change, add `--forcerun run_layer_depth_pilot`: every depth job then starts its
inner run, which recomputes only what Snakemake sees as outdated ([running guide](running_and_troubleshooting.md), section 2). Edits to a script
that Snakemake does not see, such as `get_embeddings.py`, are not picked up that way: first delete
the outputs of the first affected rule in each depth directory, for example
`results/tests/layer_depth_pilot_*/results/language_models/*/embeddings/*.parquet` after a change
to `get_embeddings.py`, which recomputes every embedding and everything downstream. Copy
`results/tests/layer_depth_pilot_<D>/results/tsv_summaries/` elsewhere first to keep the previous
numbers.

## Changes

### 2026-11-25 17:30 — guide created

Created to hold, for every test outside the main pipeline, how to run it, its settings, what it
does, its outputs and how to rerun it. The layer-depth pilot section moved here from the running
guide, with the pilot's Snakefile now at `workflow/additional_tests/layer_depth_pilot/`; its
content is otherwise unchanged.
