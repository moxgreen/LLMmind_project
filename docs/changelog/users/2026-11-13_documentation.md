# 2026-11-13 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Fix of the model-level p-values checked on the model-to-model comparisons (documentation)
- Stricter multiple-testing check removed from the documentation (documentation)
- The regional crossover analysis has its own documentation page (documentation)

---

## 12:03 — Fix of the model-level p-values checked on the model-to-model comparisons

Kind: documentation

The model-to-model results rebuilt after the p-value fix of 2026-11-09 were checked and are correct.
Some of their p-values changed slightly, but no model pair changes significance in the figures.
Nothing needs to be rerun.

---

## 12:20 — Stricter multiple-testing check removed from the documentation

Kind: documentation

The statistics reference no longer reports how many results also survive the Benjamini-Yekutieli
correction, a stricter alternative to Benjamini-Hochberg. Benjamini-Hochberg remains the correction
used in every figure; nothing in the results changed.

---

## 12:45 — The regional crossover analysis has its own documentation page

Kind: documentation

The collaborator's analysis comparing every model type with every brain region (Caption Scene) and
the language region with the whole cortex (Narratives) is now described in
`docs/reference/regional_crossover.md`, in the same format as the other reference pages. Its numbers
were recomputed from the pipeline's results and match. The page also explains what the analysis does
not show yet. It replaces `docs/regional_test_summary.md`, which can be deleted.
