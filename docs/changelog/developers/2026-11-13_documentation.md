# 2026-11-13 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Tie fix verified on the model-model tests (documentation)

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
