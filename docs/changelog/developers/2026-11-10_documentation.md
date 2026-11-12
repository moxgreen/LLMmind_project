# 2026-11-10 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Tie fix verified; dependence check of `statistics.md` recomputed with the fixed p-values (documentation)

---

## 19:07 — Tie fix verified; dependence check recomputed

Kind: documentation

The fix of 2026-11-09 14:32 (`compute_model_level_empirical_p_value()` on integer sums, see that
day's changelog) was verified against the rebuilt summary TSVs, and the documentation that still
used pre-fix p-values was updated:

- `docs/reference/statistics.md`, section 5, "Check under arbitrary dependence": study-wide BH/BY
  counts of the nearest-neighbour families recomputed from the new `model_level_empirical_p_value`
  (whole cortex 292/244 → 286/241, language region 38/0 → 37/0, visual region 126/104 → 125/104;
  Spearman rows unchanged); per-configuration text: Nature Stories under Spearman similarity BH → BY
  now 3 → 1 (was 6 → 3), language-region Narratives under cosine 18 → 0 (was 20 → 0). The
  "before the fix" caveat and the date were removed from the body; a `## Changes` entry records them.
- Section 3 already described the integer-sum comparison; section 8 ("Why the similarity types
  differ on Narratives") already counted ties exactly and matches the new TSVs (4 / 3 / 23 models
  with p < 0.05 under the published ISC).

### Context

- Request: the user asked whether the P2 rerun had finished, then asked to complete S2
  (verification, TODO cleanup, documentation, manuscript numbers).
- Files: `docs/reference/statistics.md`, both 2026-11-09 and 2026-11-10 changelogs,
  `docs/AI_USAGE.md`.
- Verification: a scratchpad script read every relabelled file, summed `common_neighbours` per
  shuffle and k, and compared with the summed `observed_common_neighbours` of the matching
  empirical p-value TSV: 0 mismatches in count and p-value for all 1224 brain-model rows. The same
  script's float-mean comparison reproduces the pre-fix study-wide counts exactly. BH via
  `compute_statistics.benjamini_hochberg()`, BY as BH × Σ1/i.
