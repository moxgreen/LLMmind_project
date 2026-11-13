# Regional crossover: each model class in each brain region

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

A collaborator asked whether the whole-cortex alignment of the language models on Caption Scene
comes from the language cortex or from the visual cortex. To answer it, they compared both model
classes with both brain regions, and checked the language models on Narratives. This page describes
what was computed, the results, what has been checked and how far the results go. The analysis is
not part of the workflow: it was run with two scripts outside the repository
(`test_caption_scene.py`, `test_narratives.py`), which read the pipeline's nearest-neighbour files.

## 1. The question

In the pipeline, every model is compared only with the region of its own modality: language models
with the language region, vision models with the visual region (see
[`brain_regions.md`](brain_regions.md), section 4; `mind_dir()` in `workflow/Snakefile` forbids the
other pairings). On Caption Scene the language models align better with the whole cortex than the
vision models do (median enrichment 1.09 vs 1.06, Spearman similarity, *k* = 125), but they are at
chance in the language region (1.001). The crossover adds the two missing pairings, to see where
that whole-cortex alignment comes from.

## 2. Method

Both scripts use the files the pipeline already writes, under Spearman similarity:

- brain neighbours: `results/{mind,language_mind,vision_mind}/{dataset}/isc_spearman_nearest_neighbours.parquet`;
- model neighbours: `results/{language,vision}_models/{dataset}/spearman_nearest_neighbours/*.parquet`.

The files are read as stored, without cutting them to a smaller *k*, so the results are for the
largest configured *k* only: 125 on Caption Scene (*n* = 1000 concepts), 5 on Narratives (*n* = 18).

1. For each concept, count the neighbours that the model and the brain region share.
2. Divide by the chance expectation *k*²/(*n* − 1), giving the concept's enrichment. This is the
   exact expectation under the relabelling null; the pipeline's enrichment plots divide by its
   Monte Carlo estimate instead ([`statistics.md`](statistics.md), section 4).
3. Average over concepts, giving one enrichment per model and region.
4. Summarise each cell by the **median over models**.
5. Bootstrap over concepts: draw *n* concepts with replacement, recompute the cells and the
   contrasts, and take the 2.5th and 97.5th percentiles as a 95% interval (Caption Scene: 2000
   iterations, seed 20261109; Narratives: 1000 iterations, seed 42).

On Caption Scene the four cells are:

| | Visual region (29 parcels) | Language region (17 parcels) |
|---|---|---|
| Vision models (14) | A | B |
| Language models (24) | C | D |

Two contrasts are tested: A − C (vision minus language models in the visual region) and the
interaction (A + D) − (B + C). On Narratives the contrast is language region − whole cortex for the
24 language models.

## 3. Results

**Caption Scene** (Spearman similarity, *k* = 125, median over models):

| | Visual region | Language region |
|---|---|---|
| Vision models | A = 1.1465 | B = 1.0115 |
| Language models | C = 1.2080 | D = 1.0010 |

| Contrast | Value | 95% bootstrap interval |
|---|---|---|
| A − C | −0.0614 | [−0.0791, −0.0448] |
| (A + D) − (B + C) | −0.0720 | [−0.0928, −0.0521] |

- Both model classes are at chance in the language region.
- In the visual region the language models score higher than the vision models.
- **Language-model families in the visual region** (median over the family's models): BLOOMZ 1.222,
  Gemma 4 1.218, Gemma 3 1.206, Gemma 2 1.205, OpenLLaMA 1.205, Gemma 3n 1.185, Gemma 1.164. Six of
  the seven are above the best vision family, CLIP (1.180).
- **Vision-model families in the visual region:** the three base CLIP models (B/16, L/14, H/14) have
  a median of 1.180 and their ImageNet fine-tuned versions 1.146; each base model scores higher than
  its fine-tuned version, under all three similarity types. DINOv2 is the lowest family (1.126),
  although under Spearman alignment, which compares all concept pairs instead of the neighbours, it
  has the highest coefficients of the vision models (ρ ≈ 0.015).

**Narratives** (Spearman similarity, *k* = 5, 24 language models, median over models):

| Brain | Enrichment |
|---|---|
| Language region | 1.5489 |
| Whole cortex | 1.5678 |
| Language region − whole cortex | −0.0189, 95% bootstrap interval [−0.3211, +0.2267] |

## 4. What has been checked

- **Recomputed on 2026-11-13** from the pipeline's files with the method of section 2: all four
  Caption Scene cells, every language-model family median and both Narratives values match to the
  fourth decimal.
- Cells A and D also agree with the pipeline's own region results
  (`results/tsv_summaries/all_model_brain_alignment_scores_{vision,language}.tsv`): 1.1464 and
  1.0008 as medians of the pipeline's enrichment, which divides by the Monte Carlo null mean.
- The CLIP and DINOv2 comparisons were checked on the same tables, under all three similarity types.
- **Not checked:** the bootstrap intervals, and the scripts themselves beyond their numbers. The
  results were first reported in a summary written by Gemini, which is replaced by this page.

## 5. Interpretation and limits

- **Visual region.** Caption Scene shows the caption (0–3 s) and then the image it describes
  (6–9 s) inside one 12 s window ([`fmri_preprocessing.md`](fmri_preprocessing.md)). The
  collaborator reads C > A as a visual response to the on-screen text ("screen reading"). The
  captions are short (4–21 words, median 10), so their visual form varies little apart from length,
  while their content names the main objects and action of the scene; at *k* = 125 out of 999 the
  neighbourhoods are coarse, so this content could be enough. Neither reading has been tested; a
  baseline built from caption length alone would separate them.
- **Language region.** Both classes are at chance, but the language region is a group-level atlas
  region that misses part of each subject's language cortex ([`brain_regions.md`](brain_regions.md),
  section 5), so this null result is ambiguous.
- **Bootstrap intervals are probably too narrow.** The bootstrap treats concepts as independent,
  but a concept's score depends on its neighbours, which are other concepts. The intervals also
  ignore which models were chosen: several models are close relatives within a family. A
  permutation of the vision/language labels across the 38 models would test the class difference
  directly.
- **Enrichment is not comparable across datasets.** Its maximum is (*n* − 1)/*k*: 3.4 on Narratives
  (*n* = 18, *k* = 5) and 8 on Caption Scene (*n* = 1000, *k* = 125). The Narratives value (1.55)
  therefore cannot be set against Caption Scene's (1.001). In concrete terms, on Narratives a story
  shares about 2.3 of its 5 nearest stories between brain and model, against 1.5 by chance.
- **Narratives, language region vs whole cortex.** The interval spans −0.32 to +0.23: no
  difference is detected, which does not show the two are equal. With 18 stories, the alignment
  may also reflect topic or length rather than language processing as such.
- **Model-level significance on Narratives depends on the similarity type.** In the pipeline's
  language-region results, 24 of 24 models are significant under Spearman similarity, 20 under
  Pearson and 18 under cosine (Benjamini-Hochberg q < 0.05).
- **Smaller claims.** The CLIP comparison rests on three pairs and one fine-tuning recipe, with no
  test, and the visual region holds early and higher visual cortex together, so it does not isolate
  low-level representations. The DINOv2 result shows that the two alignment measures rank the
  vision models differently; its Spearman coefficients are small. The family comparison is
  descriptive: models within a family are not independent.
- **Only Spearman similarity and the largest *k*.** Whether the crossover holds under cosine and
  Pearson similarity and at smaller *k* is not known.

## Changes

### 2026-11-13 12:45 — page created from the collaborator's summary

This page replaces `docs/regional_test_summary.md`, a summary of the collaborator's analysis written
by Gemini. The results are kept, the method is described from the two scripts, the numbers were
recomputed from the pipeline's files, and the interpretation was revised: the summary presented the
screen-reading reading, the Narratives "redemption" and the CLIP fine-tuning effect as established,
and called the bootstrap intervals and the Narratives result robust. Two details were added or
corrected: the cells are medians over models of the concept means (the summary did not say so),
and the Caption Scene bootstrap used 2000 iterations (the summary said 1000).
