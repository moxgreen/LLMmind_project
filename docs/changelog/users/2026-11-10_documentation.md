# 2026-11-10 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Statistics page updated to the fixed p-values (documentation)

---

## 19:07 — Statistics page updated to the fixed p-values

Kind: documentation

The fix of the model-level p-values (see the 2026-11-09 changes) was checked against the rebuilt
results and matches exactly. The statistics page, section 5, counted significant results under a
stricter correction using the old p-values; those counts now use the fixed ones. A few results
drop: across the whole cortex 286 nearest-neighbour results survive the usual correction (was 292)
and 241 the stricter one (was 244). Nature Stories under Spearman similarity keeps 1 of 3 corrected
results under the stricter correction.
