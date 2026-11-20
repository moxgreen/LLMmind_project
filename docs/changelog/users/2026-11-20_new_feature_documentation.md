# 2026-11-20 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Intermediate layers are normalised before averaging; Gemma 3n works in the depth pilot (new feature, documentation)
- Extreme values in model embeddings are capped (new feature, documentation)

---

## 16:00 — Intermediate layers are normalised before averaging; Gemma 3n works in the depth pilot

Kind: new feature, documentation

When a language model is read at an intermediate layer (the layer-depth pilot), each word piece's
internal state is now scaled the same way the model scales it after its last layer, before the
states are averaged into one vector per story. Before, a few word pieces with huge values could
dominate the average and make all stories look alike. The two Gemma 3n models, which failed
before, can now be read at intermediate layers and are back in the pilot. Results at the final
layer are unchanged. To recompute an existing pilot folder, add `--forcerun get_embeddings` to
the command (see the running guide); this overwrites that folder's summary tables.

---

## 16:20 — Extreme values in model embeddings are capped

Kind: new feature, documentation

Before model and brain representations are compared, every value of a model's story or image
vectors is now limited to a cap (the typical 95th percentile of their absolute values), as in
Huh et al. 2024. This keeps a few extremely large values from dominating the comparison. Brain
data are not changed. All brain-model and model-model scores change slightly once recomputed;
existing results are not recomputed automatically, and the running guide gives the command to
recompute them. Until then, do not mix old and new results.
