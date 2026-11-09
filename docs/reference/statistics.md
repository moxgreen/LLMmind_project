# Statistics: alignment scores, null distributions, tests and figures

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

This page describes how the workflow measures brain-model and model-model alignment, how it tests
it, and what the figures show. It is written from the code (`workflow/libraries/` and the
`llm_mind_alignment/`, `llm_llm_alignment/`, `spearman_alignment/` and `visualisation/`
scripts). Use it as the source for the methods section.

Notation: *n* concepts (stimuli) per dataset, *k* nearest neighbours, *N* relabellings
(`number_of_relabellings` in `config/config.yaml`, 10,000), random seed `random_seed` (37).

## 1. Alignment score

For each concept, both representations (the brain's ISC vectors and a model's embeddings, or two
models' embeddings) give a set of *k* nearest neighbours among the other *n* − 1 concepts, under
one similarity type (cosine, Pearson or Spearman). The concept's **alignment score** is the number
of neighbours the two sets share, divided by *k*, so it lies in [0, 1]
(`compute_alignment.compute_alignment_scores()`). The **model-level alignment score** is the mean
over concepts.

## 2. Relabelling null

The null hypothesis is that the two representations are unrelated beyond chance. It is built by
permuting the concept labels of one side:

- **LLM-brain:** the brain side stays fixed and the model's labels are permuted. **LLM-LLM:** the
  first model stays fixed and the second model's labels are permuted.
- In shuffle *i*, concept *c* receives the neighbour set of concept π(*c*), with every neighbour
  renamed through the same permutation π (`compute_nearest_neighbours.relabel_nearest_neighbours()`).
  The neighbourhood structure of the permuted side is therefore preserved; only its link to the
  concept labels is broken.
- One permutation per shuffle is reused for every *k*
  (`compute_relabelled_alignment.compute_relabelled_common_neighbours_for_all_k()`).
- **Random stream:** every null (alignment score, enrichment, Spearman) draws its *N*
  permutations in sequence from one `numpy.random.default_rng(random_seed)` stream
  (`compute_relabelled_alignment.compute_relabelled_common_neighbours_for_all_k()` and the
  Spearman script). Every test only draws `permutation(n)`, so the alignment and Spearman tests of
  a dataset use exactly the same permutations, and all models share them on purpose (a paired
  design). A replication run only needs a different seed.

## 3. Tests of the alignment score

All tests are one-sided (upper tail): they ask whether the alignment is larger than chance.

| Test | Level | Statistic | p-value | Output column |
|---|---|---|---|---|
| Empirical | concept | the concept's alignment score | (*b* + 1)/(*N* + 1), *b* = number of relabellings whose score for that concept is ≥ the observed one | `empirical_upper_tail_p_value` (per-concept TSV) |
| Hypergeometric | concept | the concept's number of common neighbours *x* | P(*X* ≥ *x*), *X* ~ Hypergeometric(population *n* − 1, *k* successes, *k* draws) | `hypergeometric_upper_tail_p_value` (per-concept TSV) |
| Empirical | model | the mean alignment score over concepts | (*b* + 1)/(*N* + 1), *b* = number of relabellings whose mean score is ≥ the observed mean, ties included | `model_level_empirical_p_value` (summary TSVs) |

The (*b* + 1)/(*N* + 1) form (`compute_statistics.empirical_upper_tail_p_value()`) counts the
observed value as one draw of the null, so a p-value is never 0; with *N* = 10,000 the smallest
possible value is about 1 × 10⁻⁴.

**Ties in the model-level test.** The null of the alignment score is discrete (every concept
score is a multiple of 1/*k*), so with few concepts many relabellings reach exactly the observed
mean, and they count towards *b*. `aggregate_alignment_scores.compute_model_level_empirical_p_value()`
therefore compares the integer sums of common neighbours over concepts, which is the same test as
comparing the means (both sides have the same concepts) but counts ties exactly. The concept-level
test compares identically computed values and counts ties as well.

The **hypergeometric expectation** of every concept's alignment score is *k*/(*n* − 1): two random
*k*-subsets of *n* − 1 concepts share *k*²/(*n* − 1) elements on average. It is the dashed
reference line of the alignment-score line plot and concept scatterplot, and the subtitle of the
alignment heatmap.

**The model-level test is `model_level_empirical_p_value`.** The six statistics
`{mean,median,min}_{empirical,hypergeom}_p_value_across_concepts` in
`results/tsv_summaries/all_model_brain_alignment_scores.tsv` and `results/tsv_summaries/all_model_model_alignment_scores.tsv`
are descriptive summaries of the per-concept p-values, **not tests**: a mean or median of
p-values has no calibrated interpretation, and the minimum is the best concept's uncorrected
p-value. They are kept on purpose (decision of 2026-09-30) but must not be reported as model-level
p-values.

## 4. Enrichment

The enrichment plots (`compute_alignment_enrichment.compute_model_alignment_enrichment()`)
express alignment relative to the relabelling null of the same model:

- **expected score** = mean relabelled alignment score over every relabelling and every concept;
- **concept-level enrichment** = observed score / expected score;
- **model-level enrichment** = mean observed score / expected score, which is exactly the mean of
  the concept-level enrichments, since both use the same expected score;
- **model-level null SD** = SD over relabellings of the mean relabelled score, divided by the
  expected score.

Enrichment = 1 means chance-level alignment.

## 5. Multiple testing

Benjamini-Hochberg q-values are computed in the plotting scripts
(`compute_statistics.benjamini_hochberg()`). **Rule: one Benjamini-Hochberg family per
(dataset, similarity type, *k*, statistic); brain-model and model-model tests are corrected
separately.** The families are:

| Family | Members | Used by |
|---|---|---|
| Brain-model alignment | `model_level_empirical_p_value` of every model, for one (dataset, similarity, *k*) | the alignment line plot, the concept scatterplot, both enrichment plots and the brain row/column of the p-value heatmap (`compute_statistics.model_level_significance()`), so their asterisks agree |
| Model-model alignment | `model_level_empirical_p_value` of every model pair, for one (dataset, similarity, *k*) | the model-model cells of the p-value heatmap |
| Spearman | model-level Spearman p-value of every model, for one (dataset, similarity) | the two Spearman plots |

There is no correction across *k* values, datasets or similarity types: the *k* values are a
sensitivity analysis, and each configuration is reported on its own. The summary TSVs contain the
uncorrected p-values only. The per-concept p-values are not corrected and not shown as asterisks.

The region analyses (language and visual region, see [`brain_regions.md`](brain_regions.md)) form
families of their own: a region's brain-model and Spearman families hold only the models of its
modality.

**Check under arbitrary dependence.** The tests of a family share the brain geometry and the
permutation stream. Benjamini-Hochberg assumes independent or positively dependent tests, which is
plausible here but not shown. Benjamini-Yekutieli (BY) holds under any dependence: its q-values are
the BH q-values multiplied by Σ 1/*i* over *i* = 1…*m*, capped at 1 (3.78 for *m* = 24, 4.21 for
*m* = 38). A one-off computation on 2026-11-09, from the p-values of the summary TSVs (before the fix
of the tie defect in section 3), counted the tests with q < 0.05:

| Family | Tests | BH | BY |
|---|---|---|---|
| All whole-cortex nearest-neighbour tests | 612 | 292 | 244 |
| All whole-cortex Spearman tests | 300 | 63 | 8 |
| All language-region nearest-neighbour tests | 360 | 38 | 0 |
| All visual-region nearest-neighbour tests | 252 | 126 | 104 |
| All language-region Spearman tests | 216 | 73 | 31 |
| All visual-region Spearman tests | 84 | 11 | 0 |

In the per-configuration families of the figures, BY removes few of the strong effects (Caption
Scene at *k* = 25 and 125: 36–38 of 38 under both; Narratives nearest neighbours under Spearman
similarity: 23 → 22; Narratives Spearman alignment under Pearson and Spearman similarity: 24 → 22
and 24 → 23). It removes the uniform, moderate ones: Narratives Spearman alignment under cosine
similarity goes from 24/24 to 0/24, because all 24 p-values lie between 0.0012 and 0.041. Caption
Scene at *k* = 5 goes from 6 to 0 (cosine) and 13 to 4 (Pearson), Nature Stories nearest neighbours
under Spearman similarity from 6 to 3, and the language-region Narratives nearest neighbours under
cosine similarity from 20 to 0.

## 6. Spearman alignment

`spearman_alignment/scripts/compute_spearman_alignment_with_empirical_p_value.py` compares the
full similarity structure instead of the neighbour sets:

- **model level:** Spearman's ρ between the brain's and the model's pairwise concept
  similarities (the upper triangle of the two *n* × *n* similarity matrices);
- **concept level:** for each concept, Spearman's ρ between its similarities to the other
  *n* − 1 concepts in the brain and in the model;
- **null:** the model's concept labels are permuted *N* times, with all permutations drawn from
  one `default_rng(random_seed)` stream, and ρ is recomputed;
- **p-value:** upper tail, (*b* + 1)/(*N* + 1) as in section 3;
- **null mean and null SD:** the mean and SD of the *N* relabelled model-level coefficients
  (`empirical_null_mean_spearman_coefficient`,
  `empirical_null_standard_deviation_spearman_coefficient`).

The expectation of this null is exactly ρ = 0, at both levels. `rank_and_normalize()` centres the
ranks, so their mean is 0. A permutation of the concepts sends every pair (i, j) to a uniformly
random pair of distinct concepts, so the expected relabelled rank of every pair is the mean rank,
0, and so is the expected ρ. At concept level, the relabelled row of a concept is a random
permutation of the centred ranks of another row, with expectation 0 again. The stored null means
agree within the Monte Carlo error of *N* = 10,000 relabellings (SD/√*N*): over all datasets,
similarity types and models, |null mean| ≤ 3.4e-4 for Caption Scene, ≤ 1.2e-4 for NSD and
≤ 3.7e-3 for Narratives and Nature Stories, whose null SD is about 0.15.

It runs once per similarity type, so with the `spearman` similarity it is a Spearman correlation
between two Spearman similarity structures: the first compares stimuli, the second compares the
brain's and the model's similarity structures.

## 7. What the figures show

| Figure | Point or box | Error bar | Grey reference |
|---|---|---|---|
| Model-level alignment line plot | mean alignment score over concepts | standard error of that mean across concepts (SD/√*n*) | dashed line at the hypergeometric expectation *k*/(*n* − 1) |
| Concept-level alignment scatterplot | one point per concept, boxplot per model | none | dashed line at *k*/(*n* − 1) |
| Model-level enrichment line plot | model-level enrichment | that model's null SD | dashed line at enrichment = 1 |
| Concept-level enrichment scatterplot | one point per concept, boxplot per model | none | dashed line at enrichment = 1 |
| Model-level Spearman line plot | model-level ρ, and a grey dash at that model's computed null mean | that model's null SD | dashed line at ρ = 0, the exact null expectation (section 6) |
| Concept-level Spearman scatterplot | one point per concept, boxplot per model | none | dashed line at ρ = 0, the exact null expectation (section 6) |
| Similarity-comparison line plots (alignment, enrichment, Spearman) | the value of the matching model-level line plot, one series per similarity type | as in that line plot (SE or null SD) | as in that line plot |
| Alignment heatmap | mean alignment score of each pair; the diagonal is blank | — | — |
| p-value heatmap | −log10 of each pair's model-level empirical p-value; the diagonal is blank | — | — |

Conventions:

- **What the error bars mean differs between plots.** In the alignment line plot, the bar is the
  standard error of the plotted mean, an uncertainty of the value. In the model-level enrichment
  and Spearman plots, the bar is the model's null SD drawn around the observed value (the y-label
  reads "± null SD"): it shows how wide chance variation is for that model, but the null
  distribution is centred on chance (enrichment = 1, ρ = 0), not on the observed value, so the bar
  is not a confidence interval and whether it reaches the reference line is not a significance
  test. The model-level Spearman line plot also marks each model's computed null mean with a grey
  dash (legend "Relabelling null mean"), which lies on the line at ρ = 0.
- **Significance is carried by asterisks:** in the model plots, black asterisks give the
  uncorrected model-level empirical p-value and blue asterisks below them the Benjamini-Hochberg
  q-value (`*` < 0.05, `**` < 0.01, `***` < 0.001); in the p-value heatmap, the asterisks give the
  q-value. Section 5 lists the families.
- The concept-level enrichment and Spearman scatterplots draw no error bars, to stay readable.
- **Similarity-comparison line plots** (`results/pictures/similarity_comparison_lineplots/`,
  `plot_similarity_comparison_lineplot.py`) put the cosine, Pearson and Spearman versions of a
  model-level line plot into one figure: one per dataset and *k* for the alignment score and the
  enrichment, one per dataset for the Spearman alignment. Each similarity type is one series in its
  own colour (`SIMILARITY_TYPE_COLOURS`: Okabe-Ito blue `#0072B2` for cosine, reddish purple
  `#CC79A7` for Pearson, sky blue `#56B4E9` for Spearman), joined by a thin line, with half-transparent
  error bars. The series sit at the same x positions, so points may overlap. They have no
  asterisks, because each series belongs to a different Benjamini-Hochberg family, and the title
  names no similarity type.

Layout, shared by all plots (constants and helpers in `libraries/visualisation_utils.py`):

- **Names.** The "scatterplots" in rule, script and folder names are concept-level boxplots with
  one point per concept; the name is historical.
- **Titles and labels.** Titles read `<level> <quantity>` (for example "Model-level brain-model
  alignment enrichment"), with `dataset: …, similarity: …, neighbours: …` on the second line.
  Y-axis labels read `<quantity> ± <error>`, or just `<quantity>` when the plot has no error bars.
- **Legend.** Inside the plot, in its top-left corner; the top quarter of the y-range is left
  empty so the legend never hides data. The heatmaps are the exception: their only legend (the
  stimulus-type colours) sits in the figure's bottom-left corner. Concept names are never listed.
- **Model order.** The same in every plot: model family (alphabetical), then number of parameters
  (`parameters_millions` in `config/config.yaml`), then model name, then stimulus type
  (`model_sort_key()` in `libraries/manage_model_metadata.py`). The order of the `models:` block
  does not matter. In the heatmaps the brain comes after all models. Every non-heatmap plot draws
  dashed vertical lines between model families.
- **Colours.** Model names show the model only (`clip_b`, not `clip_b-vision`), coloured by
  stimulus type: dark orange (`#A84800`) for language, dark green (`#007A5A`) for vision, black
  for the brain (`STIMULI_TYPE_COLOURS`), on both axes of the heatmaps. In the model-level line
  plots the points take the same colour, as circles (language) or squares (vision). Boxes are not
  coloured. Concept-level plots give each concept the same colour for every model in the plot.
- **Colour-vision deficiency.** The stimulus-type pair passes a colour-blindness simulation
  (protan, deutan, tritan) with ≥ 5:1 contrast on white, the heatmaps use `viridis`, and red is
  avoided for the q-value asterisks and the degenerate-box marker. The per-concept colours are
  the exception: with 11 to 1,000 concepts, no palette keeps them distinguishable.
- **Degenerate boxes.** In the three concept-level plots (alignment, enrichment, Spearman), a box
  whose median coincides with its first or third quartile, or whose two quartiles coincide, is
  drawn partly or wholly flat and is easy to miss; a black diamond at the median marks it
  (`mark_degenerate_boxplot_statistics()`). This is common at small *k*, where the alignment scores
  take only the values 0, 1/*k*, 2/*k*, …, so the diamond does not mean that the values have no
  spread.
- **Shared y-axes.** The model-level alignment line plot and the concept-level alignment plot of
  one dataset/similarity/*k* share the y-range `[0, 1]` (plus legend space), so they can be
  compared side by side. The two enrichment plots share one range too, computed from both
  (`enrichment_ylim()` in `libraries/compute_alignment_enrichment.py`) so that every concept,
  model-level value and its error bar fits. Their y-axis is linear from 0 to 1 and log10 above 1
  (matplotlib `symlog`, `set_enrichment_y_scale()`), with [0, 1] as tall as one decade, so a few
  very high concepts don't squash the rest. Its ticks, and so its gridlines, are 0, 0.25, 0.5,
  0.75, then 1, 2, 5, 10, … above 1; when fewer than four of them fall in the y-range (a narrow
  data-fitted range, see below), evenly spaced round ticks are used instead, so the scale stays
  readable. Because the range must fit the highest concepts, the
  model-level null-SD error bars (about 0.05) are often shorter than the markers; the shared range
  is kept on purpose, so the two plots stay comparable.
- **Data-fitted y-axes.** The similarity-comparison line plots have no concept-level counterpart,
  so their y-range is fitted to their own data (`data_fitted_ylim()`): from the lowest to the
  highest error-bar end of the three series and the reference line, plus 5% padding and the legend
  space. The alignment plot does not use the fixed `[0, 1]` range, the Spearman plot is not
  symmetric around 0, and the enrichment plot keeps the symlog axis, fitted on the axis positions
  and starting at 0 at the lowest.

## 8. Robustness checks of the whole-cortex results

One-off checks made on 2026-11-05, from the existing summary tables, ISC tables and embeddings;
they are not pipeline rules and change no result. Unless stated, each permutation null uses
*N* = 10,000 and seed 37, and Benjamini-Hochberg (BH) q-values use the families given below. Every
RSA check first reproduced the published coefficients to within 10⁻⁵. Numbers below give cosine /
Pearson / Spearman.

### Model size

Spearman's ρ between log10(`parameters_millions`) and the outcome (RSA coefficient or
nearest-neighbour enrichment) for each configuration: 24 per modality. The test is two-sided around
the null mean, permuting parameter counts within families (`model_family()`; CLIP and fine-tuned
CLIP are separate). BH runs across the 24 configurations of a modality.

| Analysis | Models | Configurations with q < 0.05 | Smallest q |
|---|---|---|---|
| Language | 24 | 0/24 | 0.396 |
| Vision | 14 | 0/24 | 0.456 |
| Language, without the 7 quantised models | 17 | 0/24 | 0.698 |

Exact tests inside a family (120 orderings, smallest p = 2/120 ≈ 0.017, uncorrected and descriptive)
reach that minimum in 2 of 24 BLOOMZ configurations (both ρ = +1) and 1 of 24 Gemma 3 configurations
(ρ = −1, where size and quantisation coincide). With 14–24 models a modest trend cannot be excluded.
This measures size, not capability.

### Dependencies between the Narratives units

The relabelling null treats the 18 Narratives units as exchangeable, but several of them share a
story, a speaker or a source, and dependent units can inflate an RSA coefficient. A permutation test
that respects these dependencies leaves no model significant, and leaving units out shows why: the
Narratives RSA rests on the two Shapes units, which stand apart from the other units in both the
brain and the model geometries. Without them no model survives correction. The leave-out checks were
chosen after seeing the restricted-permutation result, so they are exploratory.

**Blocks.** Units sharing a story, speaker or production source form four blocks: {`pieman`,
`piemanpni`, `bronx`, `slumlordreach`, `notthefallintact`, `black`}, Milky Way (3 units),
{`merlin`, `sherlock`} and Shapes (2 units). Five units have no listed relation.

Speakers and sources of the 18 units, from Nastase et al. (2021), *Scientific Data* 8:250,
"Stimuli" section ([PMC8479122](https://pmc.ncbi.nlm.nih.gov/articles/PMC8479122/)). "Not named"
means the paper does not name the speaker.

| Unit | Story | Speaker | Source | Block |
|---|---|---|---|---|
| `pieman` | Pie Man | Jim O'Grady | live at The Moth | Moth / O'Grady |
| `piemanpni` | Pie Man (PNI) | Jim O'Grady | recorded in the scanner at PNI | Moth / O'Grady |
| `bronx` | Running from the Bronx | Jim O'Grady | recorded in the scanner at PNI | Moth / O'Grady |
| `slumlordreach` | Slumlord + Reach for the Stars | Jack Hitt; Richard Garriott | live at The Moth (one run, two stories) | Moth / O'Grady |
| `notthefallintact` | It's Not the Fall that Gets You | Andy Christie | live at The Moth | Moth / O'Grady |
| `black` | I Knew You Were Black | Carol Daniel | live at The Moth | Moth / O'Grady |
| `milkywayoriginal` | Milky Way | not named (one PNI member) | written by an affiliate of the experimenters | Milky Way |
| `milkywaysynonyms` | Milky Way, synonyms version | as above | as above | Milky Way |
| `milkywayvodka` | Milky Way, vodka version | as above | as above | Milky Way |
| `merlin` | Merlin | a participant's spoken recall | recall of a TV episode | Merlin / Sherlock |
| `sherlock` | Sherlock | a participant's spoken recall | recall of a TV episode | Merlin / Sherlock |
| `shapesphysical` | Shapes, physical description | not named | describes the animation "When Heider Met Simmel" | Shapes |
| `shapessocial` | Shapes, social description | not named | describes the same animation | Shapes |
| `21styear` | The 21st Year | Christina Lazaridi (author) | written for the study | none |
| `forgot` | The Man Who Forgot Ray Bradbury | Neil Gaiman (author) | live reading, Aladdin Theater, Portland | none |
| `lucy` | Lucy | not named | WNYC public radio (2010) | none |
| `prettymouth` | Pretty Mouth and Green My Eyes | a professional actor | J. D. Salinger, *The New Yorker* (1951) | none |
| `tunnel` | Tunnel Under the World | not named | Frederik Pohl, *X Minus One* radio (1956) | none |

The Moth / O'Grady block joins two kinds of link: `pieman`, `piemanpni` and `bronx` share a
speaker, and `pieman`, `slumlordreach`, `notthefallintact` and `black` share The Moth as their
source. The paper does not say whether one participant recalled both `merlin` and `sherlock`;
they are grouped as spoken recalls from the same lab and procedure.

**The Shapes units** are not stories: `shapesphysical` and `shapessocial` describe the same
moving-shapes animation ("When Heider Met Simmel") in physical or in social terms
(`stimuli/transcripts_renamed/shapes*.txt`). They have the lowest mean similarity rank to the other
units in the model geometry, and among the lowest in the brain geometry (only `lucy` falls between
them under cosine). What makes them stand apart in the brain has not been tested.

**Restricted permutations** on all 18 units use the 240 permutations that permute the five unrelated
units and optionally swap {`merlin`, `sherlock`} with the Shapes block; the other two blocks stay
fixed, so 36 of the 153 pairs never change. No model reaches q < 0.05 (uncorrected p < 0.05: 2 / 1 / 1
of 24), and the smallest attainable p is 1/240 ≈ 0.004. Both ways of pairing the swapped units give
the same p-values. No swapped permutation reaches the observed ρ (null mean about 0.0–0.1), whereas
the unswapped ones have about the observed ρ (null mean 0.43 / 0.48 / 0.57, median 60–70 of 120 at
least as large), which is what the Shapes dependence predicts.

**Leave-out checks.** To find which units drive the result, the published RSA was recomputed without
single units and blocks:

| Check | ρ, median over models | Models with q < 0.05 |
|---|---|---|
| All 18 units (published) | 0.395 / 0.469 / 0.550 | 24 / 24 / 24 |
| Without the 20 pairs inside a block (133 pairs) | 0.378 / 0.498 / 0.542 | not tested |
| One unit per block, 72 subsets of 9 units | 0.392 / 0.489 / 0.499 | 0.8% / 12.0% / 8.9% of model-subset tests |
| Without any one non-Shapes unit (17 units) | 0.388–0.478 / 0.461–0.530 / 0.545–0.614 | 24 / 24 / 23–24 |
| Without `shapesphysical` (17 units) | 0.212 / 0.287 / 0.381 | 0 / 0 / 22 |
| Without `shapessocial` (17 units) | 0.281 / 0.324 / 0.418 | 0 / 0 / 23 |
| **Without both Shapes units (16 units)** | **−0.008 / 0.030 / 0.156** | **0 / 0 / 0** |
| Without `merlin` and `sherlock` (16 units) | 0.459 / 0.561 / 0.645 | 24 / 24 / 24 |
| Without the Shapes units, `merlin` and `sherlock` (14 units) | 0.079 / 0.129 / 0.268 | 0 / 0 / 19 |
| Without Milky Way (15 units) | 0.427 / 0.515 / 0.540 | 24 / 24 / 24 |
| Without the 6-unit block (12 units) | 0.494 / 0.549 / 0.613 | 23 / 24 / 23 |

BH runs across the 24 models for each similarity type and unit set. Removing any other unit or block
leaves the result in place; removing both Shapes units removes it, so the RSA largely reflects the
Shapes units standing apart in both geometries. Every 72-subset test keeps one Shapes unit, so its
stable coefficient does not show independence from them. Its low significance rates also reflect its
36 pairs. Keeping 16 units leaves 120 pairs, so the loss without Shapes is a fall in the coefficient,
not only a loss of power. The nearest-neighbour results were not repeated without Shapes.

### Duration and length

For Narratives (scan length 7.35–56.2 min, 18 units) and Nature Stories (9.70–14.33 min, 11 units).
Duration is the shortest scan length entering a story's ISC × TR; the covariate is −|Δlog duration|,
or −|Δlog `n_tokens`| for each model's own token counts. Partial RSA removes the covariate from the
rank-transformed brain and model similarities and relabels the model residuals; BH runs across the
24 models of each similarity type.

| Dataset | Published ρ | ρ controlling for duration | ρ controlling for tokens | Models with q < 0.05: published, duration, tokens |
|---|---|---|---|---|
| Narratives | 0.395 / 0.469 / 0.550 | 0.395 / 0.469 / 0.549 | 0.403 / 0.475 / 0.555 | 24 / 24 / 24 in all three |
| Nature Stories | 0.099 / 0.168 / 0.196 | 0.106 / 0.181 / 0.242 | 0.073 / 0.143 / 0.195 | 0 / 0 / 1; 0 / 0 / 2; 0 / 0 / 1 |

Duration similarity does not predict brain geometry (one-sided upper-tail p ≥ 0.79 in Narratives,
≥ 0.17 in Nature Stories) or any model's geometry (no q < 0.05). Mean ISC per story is not associated
with duration (ρ = 0.18, p = 0.48 and ρ = −0.12, p = 0.73) or with mean tokens (ρ = −0.003, p = 0.99
and ρ = 0.15, p = 0.66); in Narratives its association with the number of subjects is ρ = 0.43,
p = 0.075. Duration and length therefore do not explain the Narratives RSA or its contrast with
Nature Stories. This is a pairwise control: it does not exclude every effect of duration on the ISC.

### Why the similarity types differ on Narratives

On Narratives at *k* = 5, local alignment is significant for almost every model under Spearman
similarity but for few under cosine or Pearson. Two explanations were tested on 2026-11-09, both
from the existing parcel time series and model neighbours: the number of subjects per story (14–75;
the leave-one-out ISC grows with it, and only Spearman similarity is insensitive to a monotonic
change of scale), and the skew of the ISC vectors across parcels (median skewness 1.74; the 17
parcels with the highest mean ISC carry a median 57% of each story's variance around its mean). For
each condition the brain neighbours and the model-level alignment of the 24 language models were
recomputed, and tested with the pipeline's relabelling null (same seed and permutations,
*N* = 10,000, ties counted exactly; see section 3), BH across the 24 models:

| Condition | Models with p < 0.05 (cosine / Pearson / Spearman) | Models with q < 0.05 |
|---|---|---|
| Published ISC | 4 / 3 / 23 | 0 / 0 / 23 |
| Every story subsampled to 14 subjects (20 seeded draws; median, range) | 18 (8–22) / 11.5 (2–22) / 23 (20–24) | 16 (0–22) / 2 (0–22) / 23 (20–24) |
| Without the 17 highest-ISC parcels | 17 / 20 / 23 | 11 / 20 / 23 |
| log(ISC + 0.05) | 16 / 21 / 23 | 3 / 21 / 23 |

The subsampled ISC was recomputed with `compute_leave_one_out_isc()`, after the same truncation to
the shortest run and averaging of repeated runs as the pipeline (the full recomputation reproduces
the published ISC exactly). The offset 0.05 makes every value positive (23 of the 3600 ISC values
are ≤ 0, the smallest −0.041); it reduces the median skewness to 0.30. The 17 parcels (label IDs 15,
16, 44, 74, 76, 77, 78, 79, 81, 116, 117, 148, 149, 183, 187, 188, 189) include 9 of the language
region: 7 of its 9 auditory parcels and 2 of its 8 language parcels.

- **Skew is the main cause for Pearson similarity.** Removing the 17 parcels or log-transforming
  brings Pearson to 20–21 of 24 corrected models, close to Spearman. These parcels, mostly auditory,
  have high ISC in every story, so they dominate every story's vector and make the stories look
  alike.
- **The number of subjects also matters for cosine similarity.** With equal numbers, cosine reaches
  a median of 18 nominally significant models, but the result varies widely between draws. Why
  cosine is more sensitive to it than Pearson was not tested; cosine does not centre the vectors,
  so a pattern shared by all stories weighs on it more.
- **Spearman similarity is stable under every condition** (23 of 24 models).

So the gap between the similarity types comes from a few high-ISC, mostly auditory parcels and, for
cosine, from the unequal numbers of subjects. One-off check; no pipeline result changed.

## Changes

Changes to the methods described above, oldest first. Each entry gives when the change happened,
what changed and why. The sections above always describe the current code.

### 2026-10-02 09:50 — one random stream for every null

Until then, shuffle *i* of the relabelling null used `default_rng(random_seed + i)`, while the
Spearman null drew from one `default_rng(random_seed)` stream. Now every null draws from one
stream (section 2), so the alignment and Spearman tests of a dataset use the same permutations.
Results computed before the full rerun of 2026-10-02 use the old scheme.

### 2026-10-05 11:10 — file renamed

Renamed from `2026-10-02_0925_statistics.md` to `statistics.md` (living reference pages carry no
date in their name); the dated note of section 2 moved to the entry above. The content was
checked against the current code (function names, columns, `config.yaml` values) and needed no
other change.

### 2026-10-06 16:30 — plot layout conventions moved here; TODO ID and attribution block removed

The plot layout conventions (titles, legends, model order, colours, degenerate boxes, shared
y-axes) moved here from the "Outputs" section of `README.md`, which now links to this page,
together with the note on Spearman alignment under the `spearman` similarity (section 6). The
TODO reference in the entry of 2026-10-02 was removed, and the AI attribution block at the end was
replaced by the note under the title.

### 2026-10-07 16:30 — null SD drawn as the error bar of the model-level points

At the developer's request, the model-level enrichment and Spearman plots now draw each model's
null SD as the error bar of its point, instead of as a grey interval "Null ± 1 SD" around the
reference line (enrichment = 1, ρ = 0), which they had done since 2026-10-02. The y-labels read
"± null SD", the y-ranges fit value + null SD, and section 7 explains that the bar is the spread
of the null, not a confidence interval.
The developer chose to keep the shared y-range of the two enrichment
plots, even though the bars are often shorter than the markers there.

### 2026-10-09 15:14 — similarity-comparison line plots

At the developer's request, new line plots show the cosine, Pearson and Spearman versions of the
model-level alignment, enrichment and Spearman line plots in one figure, so the effect of the
similarity type is visible at a glance. Section 7 describes them; the existing plots did not
change.

### 2026-10-12 09:51 — degenerate-box marker described as the code draws it

Section 7 said the diamond marks boxes with no spread, in the alignment and Spearman plots. The
code also marks a box whose median equals one of its quartiles, which is frequent at small *k*,
and does so in the enrichment plot too; the text now says this. The heading of this section lost
its number, like the other living documents. No plot changed.

### 2026-10-13 17:50 — Spearman null drawn from the computed null

The dashed reference line of the Spearman plots was a constant ρ = 0 and nothing said why.
Section 6 now shows that 0 is the exact expectation of the relabelling null and reports the
measured null means. The model-level Spearman line plot now draws each model's computed null mean
± null SD in grey, instead of the null SD around the observed ρ; the dashed line at 0 stays. The
other plots did not change.

### 2026-10-13 18:21 — Spearman error bars back on the observed ρ

At the developer's request, the model-level Spearman line plot again draws the null SD around the
observed ρ, as before 17:50. The grey dash at each model's computed null mean stays, now without
a bar.

### 2026-10-14 15:30 — families of the region analyses

Section 5 now says that the brain-model and Spearman results of the language and visual regions,
added on this day, form their own families, with the models of one modality only.

### 2026-10-14 17:45 — summary tables moved to `results/tsv_summaries/`

The summary tables (`all_*.tsv`) are now written to `results/tsv_summaries/` instead of
`results/`; the paths on this page were updated.

### 2026-10-14 18:50 — more ticks on narrow enrichment axes

The enrichment y-axis used only the fixed ticks 0, 0.25, 0.5, 0.75, 1, 2, 5, …. On the
similarity-comparison enrichment plots, whose range is fitted to the data and can be as narrow as
0.97–1.05, this left only the tick at 1, hidden under the reference line, so the scale could not
be read. When fewer than four fixed ticks fall in the range, evenly spaced round ticks are now
used.

### 2026-11-05 18:20 — robustness checks recorded

New section 8 records one-off checks of model size, dependencies between the Narratives units,
and story duration and length. They change no pipeline result. The main finding is that the
Narratives RSA depends on the two Shapes units.

### 2026-11-09 10:00 — speakers of the Narratives units

The section on dependencies between the Narratives units named its four blocks but did not say
which speaker or source links the units in each block. A table now lists the speaker and source
of each of the 18 units, taken from the Narratives data paper, and the block it belongs to.

### 2026-11-09 14:30 — ties in the model-level test, Benjamini-Yekutieli check, Narratives similarity types

Section 3 now describes a defect found during the Narratives check below: the model-level
nearest-neighbour p-value misses ties with the observed mean, so it is too small where the null is
coarse. Section 5 records how many corrected effects survive Benjamini-Yekutieli, which holds under
any dependence between the tests. Section 8 gains a subsection testing why Narratives local
alignment depends on the similarity type: mostly the skew of the ISC vectors, and for cosine also
the unequal numbers of subjects.

### 2026-11-09 16:06 — Narratives dependency check reordered

The subsection on dependencies between the Narratives units listed the leave-out results before the
restricted-permutation result that motivated them, and did not say why dependent units matter. It
now opens with the reason for the check, its finding and its exploratory status, describes the
Shapes units in their own paragraph, and gives the restricted permutations before the leave-out
checks. No number changed.
