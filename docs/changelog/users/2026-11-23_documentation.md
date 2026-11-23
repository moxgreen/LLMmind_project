# 2026-11-23 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Layer-depth pilot documentation updated after the latest run (documentation)

---

## 10:00 — Layer-depth pilot documentation updated after the latest run

Kind: documentation

The layer-depth pilot now runs at five depths (25%, 50%, 67%, 75% and 100% of each model) on
both Narratives and Nature Stories. The running guide describes this setup, including how to copy
the brain results of both datasets into each pilot folder, how many jobs to expect (1352 per
depth) and how long a depth takes (about 1 h 20 min on node5).

The 100% pilot reads exactly the same model vectors as the main pipeline, for every model. Its
results differ from the main results only because model values are now capped. The model
embeddings page gives the size of that effect: small on Narratives, larger on Nature Stories.

The times of the 2026-11-20 changes were corrected (12:10 and 12:15 instead of 16:00 and 16:20).
