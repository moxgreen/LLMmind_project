# 2026-11-13 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Tie fix verified on the model-model tests (documentation)
- Benjamini-Yekutieli check removed from the statistics reference (documentation)
- Regional crossover summary rewritten as a reference page (documentation)

---

## 12:03 — Tie fix verified on the model-model tests

Kind: documentation

Completes the verification of the 2026-11-09 14:32 fix (`compute_model_level_empirical_p_value()`
on integer sums); the brain-model part is in the 2026-11-10 changelog. No code or result changed.

- `results/tsv_summaries/all_model_model_alignment_scores.tsv`: for all 8802 model-model tests,
  `model_level_number_of_null_scores_at_least_as_large` equals the independently recomputed
  integer count and `model_level_empirical_p_value` equals (*b* + 1)/(*N* + 1).
- 268 of the 8802 p-values differ from the old float comparison. No per-(dataset, similarity, k)
  family changes its number of tests with p < 0.05 or BH q < 0.05, so the model-model cells of the
  p-value heatmaps keep their significance. Only Benjamini-Yekutieli, which no figure uses, loses
  pairs on Nature Stories at k = 3: cosine 221 → 207, Pearson 221 → 207, Spearman 258 → 256 of 276.

### Context

- Request: the user asked whether the P2 check had finished; S2 required the new counts to be
  verified for every test before the TODO entry is closed.
- Files: both 2026-11-13 changelogs, `docs/AI_USAGE.md`. TODO P2/S2 removed.
- Verification: scratchpad script (detached run, 4038 relabelled LLM-LLM files, about 43 GB) summed
  `common_neighbours` per shuffle and k and compared with the summed `observed_common_neighbours` of
  the matching empirical p-value TSV: 0 mismatches in count and in p-value; all 8802 TSV rows
  matched one-to-one.

---

## 12:20 — Benjamini-Yekutieli check removed from the statistics reference

Kind: documentation

`docs/reference/statistics.md`, section 5: the subsection "Check under arbitrary dependence" (the
one-off BH vs BY counts, study-wide and per configuration) is removed, and a `## Changes` entry
records why. Benjamini-Hochberg (`compute_statistics.benjamini_hochberg()`) remains the only
correction; no code or result changed. The BY numbers stay in the 2026-11-09 and 2026-11-10
changelogs.

### Context

- Request: the developer decided to keep BH only, judging BY too conservative for the experiment,
  and to remove the BY check completely; it would be redone only if a reviewer asks.
- Files: `docs/reference/statistics.md`, both 2026-11-13 changelogs, `docs/AI_USAGE.md`.
- Verification: no other living document mentions Benjamini-Yekutieli (searched `README.md` and
  `docs/`).

---

## 12:45 — Regional crossover summary rewritten as a reference page

Kind: documentation

- New living document `docs/reference/regional_crossover.md`, replacing
  `docs/regional_test_summary.md` (a Gemini-written summary of a collaborator's analysis, made with
  `test_caption_scene.py` and `test_narratives.py`, outside the repository). Sections: question,
  method (from the scripts: shared neighbours / (k²/(n − 1)), mean over concepts, median over
  models, concept bootstrap: 2000 iterations, seed 20261109 for Caption Scene; 1000, seed 42 for
  Narratives), results, checks, interpretation and limits, `## Changes`.
- Corrections to the summary: the cells are medians over models (not stated); the Caption Scene
  bootstrap used 2000 iterations, not 1000; the interpretation (screen reading, Narratives
  "redemption", CLIP fine-tuning as causal, robust intervals) is presented as untested.
- `README.md`: one index line. `docs/AI_USAGE.md`: new row, README date.
- The old `docs/regional_test_summary.md` is still on disk: deleting it was not permitted to Claude
  and is left to the developer.
- `.claude/SUGGESTIONS/LLMmind_project.md`, I26/IS26: path updated to the new page.

### Context

- Request: the developer asked to bring `regional_test_summary.md` into the format of the other
  documentation.
- Files: `docs/reference/regional_crossover.md`, `README.md`, `docs/AI_USAGE.md`, both 2026-11-13
  changelogs.
- Verification: a scratchpad script recomputed, from the pipeline's Spearman nearest-neighbour
  parquets, the four Caption Scene cells at k = 125 (1.1465, 1.0115, 1.2080, 1.0010), the seven
  language-model family medians in the visual region and the Narratives values at k = 5 (1.5489,
  1.5678): all match the summary to four decimals. The bootstrap intervals were not recomputed.
