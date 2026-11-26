# 2026-11-26 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Five extra analyses can now be rerun from the repository as additional tests (new feature, documentation)
- The effect of the start-of-text token on the language models was measured: it changes no result (documentation)
- The concept-level plots are now called boxplots, in their folder names too (refactor, documentation)
- New plots of alignment enrichment against model size, and a table of the size trend within each model family (new feature, documentation)
- The layer-depth pilot no longer recomputes the last layer, which gave the same results as the main analysis (removal, documentation)

---

## 12:00 — Five extra analyses can now be rerun from the repository

Kind: new feature, documentation

- The checks behind several numbers in the documentation used to be one-off scripts that nobody
  could rerun. They are now additional tests in `workflow/additional_tests/`, next to the
  layer-depth pilot:
  - the Narratives dependency checks (does the Narratives RSA survive related stories?);
  - the duration and length controls;
  - the check of why the similarity types differ on Narratives;
  - the overlap between the NSD and Caption Scene images;
  - the collaborator's regional crossover, which gives exactly the collaborator's numbers.
- They never run with the main pipeline. To run them all, one after the other:

  ```bash
  for test in narratives_dependencies duration_length_controls similarity_type_check image_overlap regional_crossover layer_depth_pilot; do
      snakemake -s workflow/additional_tests/$test/Snakefile --use-conda --cores 4 --resources gpu=1 || break
  done
  ```

  All but the pilot take about 13 minutes together; the pilot takes about 6 h 30 min and needs the
  GPU. Each writes its tables to `results/tests/<test>/`. How to run each one is in
  `docs/guides/additional_tests.md`.
- The documented numbers were replaced by the tests' results on the current outputs. Most moved
  slightly, because the model similarities now cap extreme embedding values. The conclusions hold:
  the Narratives RSA still rests on the two Shapes stories, and duration and length still explain
  none of it. One conclusion changed: removing the few highest-ISC parcels now helps cosine as much
  as Pearson, so skew explains most of the gap between the similarity types.

---

## 14:45 — The start-of-text token changes no result

Kind: documentation

- Each language model reads a special start-of-text token (BOS) before every text, and its output
  for that token was included in the text's vector. This was flagged as a possible distortion,
  especially for the short Caption Scene captions.
- A one-off check removed it from the vectors of all 24 language models and recomputed the
  alignment.
  - About 97% of each concept's nearest neighbours stay the same.
  - Alignment scores change by at most 0.011.
  - Every model that was significant after correction stays significant, and none becomes so.
- The pipeline therefore stays as it is. The details are in `docs/reference/model_embeddings.md`,
  section 3.

---

## 17:30 — Concept-level plots are now called boxplots

Kind: refactor, documentation

The concept-level plots were called "scatterplots" although they are boxplots with one point per
concept. Their folders in `results/pictures/` are now `concept_alignment_boxplots/`,
`concept_alignment_enrichment_boxplots/` and `concept_spearman_alignment_boxplots/` (and their
`_language` and `_vision` versions). The plots themselves do not change. The next pipeline run
draws them into the new folders, which takes about 20 minutes and recomputes no data. The old
`*_scatterplots` folders have been deleted.

---

## 17:30 — Alignment enrichment against model size

Kind: new feature, documentation

The pipeline now shows whether larger models align better with the brain:

- `results/pictures/model_size_lineplots/`: one plot per dataset, similarity measure and number of
  neighbours. Each point is a model, at its number of parameters (x) and its alignment enrichment
  (y); the models of a family share a colour and are joined in order of size; every point is
  labelled with the model's name.
- `results/tsv_summaries/model_size_within_family_spearman.tsv`: for each of those settings and
  each family of at least three models, Spearman's ρ between enrichment and size (+1 means that
  enrichment always grows with size, −1 that it always falls). It is descriptive: with three to
  five models per family no trend can be significant.

This replaces the earlier one-off model-size test, which no script in the repository reproduced.

---

## 16:40 — The layer-depth pilot no longer recomputes the last layer

Kind: removal, documentation

- The layer-depth pilot now reads the models at 25%, 50%, 67% and 75% of their depth only. Reading
  them at 100% gave exactly the same numbers as the main analysis (checked value by value), so it
  only cost about 1 h 20 min of GPU time.
- For the comparison with the last layer, use the main results in `results/tsv_summaries/`,
  keeping only the 21 BLOOMZ and Gemma models of the pilot. The numbers quoted for 100% depth do
  not change.
- The old folder `results/tests/layer_depth_pilot_100/` was deleted; if you have a copy elsewhere,
  it is safe to delete too.
- Running every additional test now takes about 5 h on the GPU instead of 6 h 30 min.
